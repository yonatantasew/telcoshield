"""
Sender ID & Financial Brand Impersonation Rules
"""

import re
from typing import Optional, Dict, Set
from .base import BaseRule
from ..models import MessageContext, NLPResult, RuleViolation, Severity

# Authorized Alphanumeric Sender IDs and Shortcodes in Ethiopia and East Africa
AUTHORIZED_FINANCIAL_REGISTRY: Dict[str, Set[str]] = {
    "telebirr": {"telebirr", "127", "ethio_telecom"},
    "cbe": {"cbe", "cbebirr", "889", "commercial_bank_of_ethiopia"},
    "mpesa": {"mpesa", "m-pesa", "safaricom"},
    "awash": {"awashbank", "awashbirr", "898"},
    "dashen": {"dashenbank", "amole"},
    "abyssinia": {"boa", "bankofabyssinia"}
}

FINANCIAL_RECEIPT_PATTERNS = [
    re.compile(r"credited\s+with\s+[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"received\s+[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"transferred\s+[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"txn\s*id\s*:\s*[a-zA-Z0-9]+", re.IGNORECASE),
    re.compile(r"transaction\s*id\s*:\s*[a-zA-Z0-9]+", re.IGNORECASE),
    re.compile(r"current\s*balance\s*:\s*[\d,]+(?:\.\d{2})?\s*ETB", re.IGNORECASE),
    re.compile(r"የሂሳብ\s*እንቅስቃሴ|ብር\s*ገቢ\s*ተደርጓል", re.IGNORECASE)
]

OTP_HARVEST_PATTERNS = [
    re.compile(r"share\s+your\s+otp", re.IGNORECASE),
    re.compile(r"send\s+your\s+otp", re.IGNORECASE),
    re.compile(r"otp\s+code", re.IGNORECASE),
    re.compile(r"verify\s+your\s+pin", re.IGNORECASE),
    re.compile(r"fayda\s+digital\s+id", re.IGNORECASE)
]


class FinancialBrandImpersonationRule(BaseRule):
    """
    Catches fake payment confirmation receipts sent from unverified personal SIMs
    (The critical Blind Spot of pure NLP models).
    """
    rule_id = "RULE-META-001"
    name = "Financial Brand Impersonation"

    def evaluate(self, ctx: MessageContext, nlp: NLPResult) -> Optional[RuleViolation]:
        normalized_sender = ctx.sender_id.strip().lower()
        normalized_text = ctx.text.lower()

        # Identify any financial institutions claimed in text
        claimed_brands = [b for b in AUTHORIZED_FINANCIAL_REGISTRY.keys() if b in normalized_text]
        is_receipt = any(p.search(ctx.text) for p in FINANCIAL_RECEIPT_PATTERNS)

        if is_receipt and claimed_brands:
            for brand in claimed_brands:
                authorized_senders = AUTHORIZED_FINANCIAL_REGISTRY[brand]
                if normalized_sender not in authorized_senders:
                    return RuleViolation(
                        rule_id=self.rule_id,
                        severity=Severity.CRITICAL,
                        title="Unverified Financial Transaction Receipt",
                        description=(
                            f"Message claims an official {brand.upper()} transaction receipt/credit, "
                            f"but originated from unauthorized sender '{ctx.sender_id}' (not in carrier whitelist)."
                        )
                    )
        return None


class CredentialHarvestingRule(BaseRule):
    """
    Detects attempts to harvest OTPs, PINs, or Fayda digital identity credentials.
    """
    rule_id = "RULE-META-002"
    name = "Credential Harvesting Pretext"

    def evaluate(self, ctx: MessageContext, nlp: NLPResult) -> Optional[RuleViolation]:
        normalized_sender = ctx.sender_id.strip().lower()
        normalized_text = ctx.text.lower()

        has_otp_pattern = any(p.search(ctx.text) for p in OTP_HARVEST_PATTERNS)
        claimed_brands = [b for b in AUTHORIZED_FINANCIAL_REGISTRY.keys() if b in normalized_text]

        if has_otp_pattern and claimed_brands:
            for brand in claimed_brands:
                if normalized_sender not in AUTHORIZED_FINANCIAL_REGISTRY[brand]:
                    return RuleViolation(
                        rule_id=self.rule_id,
                        severity=Severity.HIGH,
                        title="Unauthorized Credential Request",
                        description=(
                            f"Message requests sensitive verification codes (OTP/PIN/Fayda) purporting to represent {brand.upper()}, "
                            f"originating from personal/unverified sender '{ctx.sender_id}'."
                        )
                    )
        return None
