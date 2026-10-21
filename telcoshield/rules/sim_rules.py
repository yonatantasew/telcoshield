"""
Mule SIM & Burner SIM Velocity Rules
"""

from typing import Optional
from .base import BaseRule
from .sender_rules import FINANCIAL_RECEIPT_PATTERNS, OTP_HARVEST_PATTERNS
from ..models import MessageContext, NLPResult, RuleViolation, Severity


class BurnerMuleSimRule(BaseRule):
    """
    Detects freshly activated SIM cards (<24 hours old) blasting financial traffic or OTP requests
    (The vector uncovered in the October 17 Federal Police 478-SIM raid).
    """
    rule_id = "RULE-MULE-SIM-001"
    name = "Burner / Mule SIM Burst Activity"

    def evaluate(self, ctx: MessageContext, nlp: NLPResult) -> Optional[RuleViolation]:
        is_fresh_sim = ctx.sim_age_hours < 24.0
        is_financial = any(p.search(ctx.text) for p in FINANCIAL_RECEIPT_PATTERNS)
        is_otp = any(p.search(ctx.text) for p in OTP_HARVEST_PATTERNS)
        contains_brand = any(b in ctx.text.lower() for b in ["telebirr", "cbe", "mpesa", "payment", "bank"])

        if is_fresh_sim and (is_financial or is_otp or contains_brand):
            return RuleViolation(
                rule_id=self.rule_id,
                severity=Severity.CRITICAL,
                title="Mule / Burner SIM Detected",
                description=(
                    f"SIM card was activated only {ctx.sim_age_hours:.1f} hours ago (<24h carrier threshold) "
                    f"and is actively generating high-risk financial or authentication traffic."
                )
            )
        return None
