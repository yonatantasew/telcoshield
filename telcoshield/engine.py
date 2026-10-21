"""
TelcoShield Decision Fusion & Security Arbitration Engine
"""

import time
from typing import List, Optional
from .models import (
    MessageContext,
    NLPResult,
    RuleViolation,
    InspectionReport,
    Verdict,
    Severity,
    IngressRoute
)
from .client import PAiCoreClient
from .rules import (
    BaseRule,
    FinancialBrandImpersonationRule,
    CredentialHarvestingRule,
    InterconnectBypassRule,
    UrlPhishingShortenerRule,
    BurnerMuleSimRule
)


class TelcoShieldEngine:
    """
    Carrier-grade security arbitration engine.
    Orchestrates deep packet/signaling inspection with AI/NLP inference.
    """

    def __init__(self, client: Optional[PAiCoreClient] = None, rules: Optional[List[BaseRule]] = None):
        self.client = client or PAiCoreClient()
        self.rules: List[BaseRule] = rules or [
            FinancialBrandImpersonationRule(),
            CredentialHarvestingRule(),
            InterconnectBypassRule(),
            BurnerMuleSimRule(),
            UrlPhishingShortenerRule()
        ]

    def register_rule(self, rule: BaseRule) -> None:
        """Dynamically add custom enterprise firewall rules"""
        self.rules.append(rule)

    def inspect(self, context: MessageContext) -> InspectionReport:
        """
        Executes hybrid inspection pipeline:
        1. Queries PAiCore mBERT for semantic classification
        2. Evaluates telecom signaling metadata rules
        3. Arbitrates decision fusion and computes composite risk score
        """
        pipeline_start = time.perf_counter()

        # Step 1: Run PAiCore NLP Inference
        nlp_result = self.client.predict(context.text)

        # Step 2: Evaluate Telecom Metadata & Signaling Rules
        violations: List[RuleViolation] = []
        for rule in self.rules:
            violation = rule.evaluate(context, nlp_result)
            if violation:
                violations.append(violation)

        # Step 3: Compute Risk Score & Severity
        max_severity = Severity.INFO
        severity_weights = {
            Severity.INFO: 0.0,
            Severity.LOW: 0.15,
            Severity.MEDIUM: 0.35,
            Severity.HIGH: 0.65,
            Severity.CRITICAL: 0.95
        }

        # Baseline score from NLP
        if nlp_result.label in ("phishing", "spam"):
            base_risk = 0.60 + (nlp_result.confidence * 0.35)
            if max_severity == Severity.INFO:
                max_severity = Severity.HIGH
        else:
            base_risk = 0.05

        # Incorporate rule violations
        rule_risk = 0.0
        for v in violations:
            rule_risk = max(rule_risk, severity_weights.get(v.severity, 0.0))
            if severity_weights.get(v.severity, 0.0) > severity_weights.get(max_severity, 0.0):
                max_severity = v.severity

        composite_risk = min(1.0, max(base_risk, rule_risk))

        # Step 4: Final Gateway Arbitration
        has_critical = any(v.severity == Severity.CRITICAL for v in violations)
        has_high = any(v.severity == Severity.HIGH for v in violations)

        if has_critical or composite_risk >= 0.70 or nlp_result.label == "phishing":
            verdict = Verdict.BLOCKED_FRAUD
            gateway_action = "DROP_AT_SMSC_AND_ALERT_SIEM"
        elif has_high or composite_risk >= 0.40:
            verdict = Verdict.FLAG_SUSPICIOUS
            gateway_action = "QUARANTINE_FOR_MANUAL_REVIEW"
        else:
            verdict = Verdict.ALLOWED
            gateway_action = "DELIVER_TO_HANDSET"

        # Check if Telecom Edge overrode an NLP false-negative
        metadata_override = (nlp_result.label == "ham" and verdict == Verdict.BLOCKED_FRAUD)

        total_latency = (time.perf_counter() - pipeline_start) * 1000

        return InspectionReport(
            context=context,
            nlp_result=nlp_result,
            verdict=verdict,
            risk_score=composite_risk,
            threat_severity=max_severity,
            violations=violations,
            metadata_override=metadata_override,
            total_latency_ms=total_latency,
            gateway_action=gateway_action
        )
