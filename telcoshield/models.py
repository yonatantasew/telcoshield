"""
TelcoShield Core Domain Models & Schemas
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


class IngressRoute(str, Enum):
    DOMESTIC_ONNET = "domestic_onnet"
    INTERNATIONAL_IPX = "international_ipx"
    BULK_AGGREGATOR = "bulk_aggregator"
    GREY_ROUTE = "grey_route"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Verdict(str, Enum):
    ALLOWED = "ALLOWED"
    FLAG_SUSPICIOUS = "FLAG_SUSPICIOUS"
    BLOCKED_FRAUD = "BLOCKED_FRAUD"


@dataclass
class MessageContext:
    """Represents the raw incoming message and associated signaling metadata"""
    sender_id: str
    text: str
    ingress_route: IngressRoute = IngressRoute.DOMESTIC_ONNET
    calling_gt: str = "+251911000000"
    sim_age_hours: float = 720.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class NLPResult:
    """Raw output from PAiCore OpenTextShield mBERT inference"""
    label: str  # 'ham', 'spam', 'phishing'
    confidence: float
    processing_time_ms: float
    model_name: str = "OTS_mBERT_v2.9"
    is_fallback: bool = False


@dataclass
class RuleViolation:
    """Individual security policy or signaling rule violation"""
    rule_id: str
    severity: Severity
    title: str
    description: str


@dataclass
class InspectionReport:
    """Unified Carrier-Grade Telecom Firewall Telemetry Report"""
    context: MessageContext
    nlp_result: NLPResult
    verdict: Verdict
    risk_score: float  # 0.0 to 1.0
    threat_severity: Severity
    violations: List[RuleViolation]
    metadata_override: bool
    total_latency_ms: float
    gateway_action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.context.sender_id,
            "message_text": self.context.text,
            "ingress_route": self.context.ingress_route.value if isinstance(self.context.ingress_route, IngressRoute) else str(self.context.ingress_route),
            "calling_gt": self.context.calling_gt,
            "sim_age_hours": self.context.sim_age_hours,
            "paicore_nlp_label": self.nlp_result.label,
            "paicore_nlp_confidence": round(self.nlp_result.confidence, 4),
            "paicore_processing_time": round(self.nlp_result.processing_time_ms / 1000, 4),
            "final_verdict": self.verdict.value if isinstance(self.verdict, Verdict) else str(self.verdict),
            "risk_score": round(self.risk_score, 2),
            "threat_severity": self.threat_severity.value if isinstance(self.threat_severity, Severity) else str(self.threat_severity),
            "rule_triggers": [f"{v.rule_id} [{v.severity.value}]: {v.title} - {v.description}" for v in self.violations],
            "metadata_override": self.metadata_override,
            "total_latency_ms": round(self.total_latency_ms, 2),
            "gateway_action": self.gateway_action,
            "timestamp": self.context.timestamp
        }
