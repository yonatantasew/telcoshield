"""
TelcoShield: Carrier-Grade Telecom Signaling Firewall & FinTech Fraud Defense
"""

from .models import (
    MessageContext,
    NLPResult,
    RuleViolation,
    InspectionReport,
    IngressRoute,
    Severity,
    Verdict
)
from .client import PAiCoreClient
from .engine import TelcoShieldEngine

__version__ = "1.0.0"

__all__ = [
    "TelcoShieldEngine",
    "PAiCoreClient",
    "MessageContext",
    "NLPResult",
    "RuleViolation",
    "InspectionReport",
    "IngressRoute",
    "Severity",
    "Verdict"
]
