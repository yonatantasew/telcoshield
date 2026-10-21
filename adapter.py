"""
TelcoShield Metadata-Correlated Adapter for PAiCore OpenTextShield
Bridges raw NLP content classification with Telecom Network Metadata (Sender ID, Ingress Route, Calling GT, SIM Age)
"""

import re
import time
import json
import urllib.request
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Whitelist of officially registered Alphanumeric Sender IDs and Shortcodes in Ethiopia/East Africa
AUTHORIZED_FINANCIAL_SENDERS = {
    "telebirr": {"telebirr", "127", "ethio_telecom"},
    "cbe": {"cbe", "cbebirr", "889", "commercial_bank_of_ethiopia"},
    "mpesa": {"mpesa", "m-pesa", "safaricom"},
    "awash": {"awashbank", "awashbirr", "898"},
    "dashen": {"dashenbank", "amole"},
    "abyssinia": {"boa", "bankofabyssinia"}
}

# Transaction receipt / financial transfer signature patterns
FINANCIAL_RECEIPT_PATTERNS = [
    re.compile(r"credited\s+with\s+[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"received\s+[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"transferred\s+[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"txn\s*id\s*:\s*[a-zA-Z0-9]+", re.IGNORECASE),
    re.compile(r"transaction\s*id\s*:\s*[a-zA-Z0-9]+", re.IGNORECASE),
    re.compile(r"current\s*balance\s*:\s*[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"የሂሳብ\s*እንቅስቃሴ|ብር\s*ገቢ\s*ተደርጓል", re.IGNORECASE)
]

# Sensitive credentials & OTP harvesting patterns
OTP_HARVEST_PATTERNS = [
    re.compile(r"share\s+your\s+otp", re.IGNORECASE),
    re.compile(r"send\s+your\s+otp", re.IGNORECASE),
    re.compile(r"otp\s+code", re.IGNORECASE),
    re.compile(r"verify\s+your\s+pin", re.IGNORECASE),
    re.compile(r"fayda\s+digital\s+id", re.IGNORECASE)
]

SUSPICIOUS_URL_REGEX = re.compile(r"https?://(?:[a-zA-Z0-9$-_@.&+!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
SHORTENER_DOMAINS = ["bit.ly", "tinyurl.com", "t.me", "wa.me", "is.gd", "cutt.ly"]


@dataclass
class InspectionResult:
    sender_id: str
    message_text: str
    ingress_route: str
    calling_gt: str
    sim_age_hours: float
    paicore_nlp_label: str
    paicore_nlp_confidence: float
    paicore_processing_time: float
    final_verdict: str  # ALLOWED | FLAG_SUSPICIOUS | BLOCKED_FRAUD
    threat_severity: str  # NONE | LOW | MEDIUM | HIGH | CRITICAL
    rule_triggers: List[str]
    metadata_override: bool
    total_latency_ms: float


class TelcoShieldAdapter:
    def __init__(self, ots_api_url: str = "http://localhost:8002/predict/"):
        self.ots_api_url = ots_api_url

    def query_paicore_ots(self, text: str) -> Dict:
        """Calls PAiCore's live OpenTextShield API"""
        payload = json.dumps({"text": text, "model": "ots-mbert"}).encode("utf-8")
        req = urllib.request.Request(
            self.ots_api_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            return {
                "label": "unknown",
                "probability": 0.0,
                "processing_time": 0.0,
                "error": str(e)
            }

    def inspect_metadata(
        self,
        sender_id: str,
        text: str,
        ingress_route: str = "domestic_onnet",
        calling_gt: str = "+251911000000",
        sim_age_hours: float = 720.0
    ) -> Dict:
        """
        Deep Telecom Network Metadata & Signaling Inspection:
        - Sender ID validation
        - Ingress Route / Interconnect Grey Route Detection (GSMA FS.11 Cat-1)
        - Calling Global Title (GT) Verification
        - Burner / Mule SIM card age detection
        """
        triggers = []
        severity = "NONE"
        normalized_sender = sender_id.strip().lower()
        normalized_text = text.lower()

        # Check which financial brands are claimed in the message body
        claimed_brands = []
        for brand in AUTHORIZED_FINANCIAL_SENDERS.keys():
            if brand in normalized_text:
                claimed_brands.append(brand)

        # -------------------------------------------------------------
        # 1. Ingress Route & Global Title Spoofing (GSMA FS.11 Cat-1)
        # -------------------------------------------------------------
        # A) Grey Route Bypass: Domestic brand arriving via international/grey route
        is_official_sender = any(normalized_sender in aliases for aliases in AUTHORIZED_FINANCIAL_SENDERS.values())
        if is_official_sender and ingress_route in ("international_ipx", "grey_route"):
            triggers.append(
                f"RULE-INTERCONNECT-001 [CRITICAL]: Domestic carrier brand '{sender_id}' arrived via '{ingress_route}'. "
                f"Classic A2P Grey Route / Global Title Spoofing attack detected."
            )
            severity = "CRITICAL"

        # B) Foreign GT injecting domestic traffic (+251)
        if ingress_route == "international_ipx" and not calling_gt.startswith("+251"):
            if any(b in normalized_text for b in ["telebirr", "cbe", "mpesa"]):
                triggers.append(
                    f"RULE-GT-002 [HIGH]: Foreign Global Title '{calling_gt}' routing domestic financial traffic via international interconnect."
                )
                if severity != "CRITICAL":
                    severity = "HIGH"

        # -------------------------------------------------------------
        # 2. Burner / Mule SIM Detection (Oct 17 478-SIM Case)
        # -------------------------------------------------------------
        is_financial_receipt = any(p.search(text) for p in FINANCIAL_RECEIPT_PATTERNS)
        has_otp_harvest = any(p.search(text) for p in OTP_HARVEST_PATTERNS)

        if sim_age_hours < 24.0:
            if is_financial_receipt or has_otp_harvest or claimed_brands:
                triggers.append(
                    f"RULE-MULE-SIM-001 [CRITICAL]: Burner/Mule SIM detected! SIM card was activated only {sim_age_hours:.1f} hours ago (<24h threshold) "
                    f"and is transmitting high-risk financial/OTP payloads."
                )
                severity = "CRITICAL"

        # -------------------------------------------------------------
        # 3. Financial Receipt Impersonation Check (Test 4 Fix)
        # -------------------------------------------------------------
        if is_financial_receipt and claimed_brands:
            for brand in claimed_brands:
                authorized_aliases = AUTHORIZED_FINANCIAL_SENDERS[brand]
                if normalized_sender not in authorized_aliases:
                    triggers.append(
                        f"RULE-META-001 [CRITICAL]: Message claims {brand.upper()} transaction receipt/credit, "
                        f"but sender '{sender_id}' is NOT an authorized shortcode for {brand.upper()}."
                    )
                    severity = "CRITICAL"

        # -------------------------------------------------------------
        # 4. OTP Harvesting Pretext Check (Test 3 Reinforcement)
        # -------------------------------------------------------------
        if has_otp_harvest and claimed_brands:
            for brand in claimed_brands:
                if normalized_sender not in AUTHORIZED_FINANCIAL_SENDERS[brand]:
                    triggers.append(
                        f"RULE-META-002 [HIGH]: OTP harvesting or Fayda verification claimed from unauthorized sender '{sender_id}'."
                    )
                    if severity != "CRITICAL":
                        severity = "HIGH"

        # -------------------------------------------------------------
        # 5. Shortened URL in Financial Context
        # -------------------------------------------------------------
        urls = SUSPICIOUS_URL_REGEX.findall(text)
        has_shortener = any(any(s in u for s in SHORTENER_DOMAINS) for u in urls)
        if has_shortener and (claimed_brands or is_financial_receipt):
            triggers.append(
                f"RULE-META-003 [HIGH]: Contains URL shortener {urls} combined with financial institution references."
            )
            if severity != "CRITICAL":
                severity = "HIGH"

        return {
            "triggers": triggers,
            "severity": severity,
            "is_override_needed": severity in ("HIGH", "CRITICAL")
        }

    def inspect_message(
        self,
        sender_id: str,
        text: str,
        ingress_route: str = "domestic_onnet",
        calling_gt: str = "+251911000000",
        sim_age_hours: float = 720.0
    ) -> InspectionResult:
        """
        Hybrid Inspection: Combines PAiCore NLP output with Telecom Metadata Rules
        """
        start_time = time.perf_counter()

        # Step 1: Query PAiCore OpenTextShield mBERT model
        ots_result = self.query_paicore_ots(text)
        nlp_label = ots_result.get("label", "unknown")
        nlp_confidence = float(ots_result.get("probability", 0.0))
        nlp_proc_time = float(ots_result.get("processing_time", 0.0))

        # Step 2: Run Telecom Metadata & Signaling Inspection
        meta_result = self.inspect_metadata(
            sender_id=sender_id,
            text=text,
            ingress_route=ingress_route,
            calling_gt=calling_gt,
            sim_age_hours=sim_age_hours
        )

        # Step 3: Decision Fusion & Arbitration
        final_verdict = "ALLOWED"
        metadata_override = False

        if meta_result["is_override_needed"]:
            final_verdict = "BLOCKED_FRAUD"
            metadata_override = (nlp_label == "ham")  # Flagged that NLP called it HAM but metadata caught it!
        elif nlp_label in ("phishing", "spam"):
            final_verdict = "BLOCKED_FRAUD"
            if meta_result["severity"] == "NONE":
                meta_result["severity"] = "HIGH"
            meta_result["triggers"].append(f"RULE-NLP-001: PAiCore mBERT classified text as {nlp_label} ({nlp_confidence*100:.1f}%)")
        else:
            final_verdict = "ALLOWED"

        total_latency = (time.perf_counter() - start_time) * 1000

        return InspectionResult(
            sender_id=sender_id,
            message_text=text,
            ingress_route=ingress_route,
            calling_gt=calling_gt,
            sim_age_hours=sim_age_hours,
            paicore_nlp_label=nlp_label,
            paicore_nlp_confidence=nlp_confidence,
            paicore_processing_time=nlp_proc_time,
            final_verdict=final_verdict,
            threat_severity=meta_result["severity"],
            rule_triggers=meta_result["triggers"],
            metadata_override=metadata_override,
            total_latency_ms=round(total_latency, 2)
        )
