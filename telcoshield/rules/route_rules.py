"""
Interconnect Route & GSMA FS.11 Cat-1 Signaling Rules
"""

import re
from typing import Optional
from .base import BaseRule
from .sender_rules import AUTHORIZED_FINANCIAL_REGISTRY
from ..models import MessageContext, NLPResult, RuleViolation, Severity, IngressRoute

SUSPICIOUS_URL_REGEX = re.compile(r"https?://(?:[a-zA-Z0-9$-_@.&+!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
SHORTENER_DOMAINS = ["bit.ly", "tinyurl.com", "t.me", "wa.me", "is.gd", "cutt.ly"]


class InterconnectBypassRule(BaseRule):
    """
    GSMA FS.11 Category 1: Inbound Domestic Brand from Foreign Link.
    Detects A2P Grey Route bypass where domestic brands (Telebirr/CBE) arrive via International IPX.
    """
    rule_id = "GSMA-FS11-001"
    name = "A2P Interconnect Grey Route Bypass"

    def evaluate(self, ctx: MessageContext, nlp: NLPResult) -> Optional[RuleViolation]:
        normalized_sender = ctx.sender_id.strip().lower()

        # Check if the sender is claiming to be an official domestic brand
        is_official_domestic = any(
            normalized_sender in aliases for aliases in AUTHORIZED_FINANCIAL_REGISTRY.values()
        )

        route_val = ctx.ingress_route.value if isinstance(ctx.ingress_route, IngressRoute) else str(ctx.ingress_route)

        if is_official_domestic and route_val in ("international_ipx", "grey_route"):
            return RuleViolation(
                rule_id=self.rule_id,
                severity=Severity.CRITICAL,
                title="GSMA FS.11 Cat-1 Interconnect Violation",
                description=(
                    f"Official domestic sender ID '{ctx.sender_id}' arrived via unauthorized route '{route_val}'. "
                    f"Classic Global Title Spoofing / Grey Route bypass attempt."
                )
            )

        if route_val == "international_ipx" and not ctx.calling_gt.startswith("+251"):
            # Foreign GT routing domestic mobile money traffic
            if any(b in ctx.text.lower() for b in ["telebirr", "cbe", "mpesa"]):
                return RuleViolation(
                    rule_id="GSMA-FS11-002",
                    severity=Severity.HIGH,
                    title="Foreign GT Routing Domestic Financial Traffic",
                    description=(
                        f"Foreign Global Title '{ctx.calling_gt}' routing Ethiopian mobile money transaction "
                        f"through international interconnect link."
                    )
                )

        return None


class UrlPhishingShortenerRule(BaseRule):
    """
    Flags URL shorteners (bit.ly, t.me) when embedded inside financial or account messages.
    """
    rule_id = "RULE-URL-003"
    name = "Obfuscated URL Shortener"

    def evaluate(self, ctx: MessageContext, nlp: NLPResult) -> Optional[RuleViolation]:
        urls = SUSPICIOUS_URL_REGEX.findall(ctx.text)
        has_shortener = any(any(s in u for s in SHORTENER_DOMAINS) for u in urls)
        claimed_brands = any(b in ctx.text.lower() for b in AUTHORIZED_FINANCIAL_REGISTRY.keys())

        if has_shortener and claimed_brands:
            return RuleViolation(
                rule_id=self.rule_id,
                severity=Severity.HIGH,
                title="Obfuscated Financial Link",
                description=(
                    f"Message embeds shortened/obfuscated redirection link(s) {urls} "
                    f"purporting to relate to mobile financial services."
                )
            )
        return None
