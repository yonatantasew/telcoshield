"""
TelcoShield Security Rules Catalog
"""

from .base import BaseRule
from .sender_rules import FinancialBrandImpersonationRule, CredentialHarvestingRule
from .route_rules import InterconnectBypassRule, UrlPhishingShortenerRule
from .sim_rules import BurnerMuleSimRule

__all__ = [
    "BaseRule",
    "FinancialBrandImpersonationRule",
    "CredentialHarvestingRule",
    "InterconnectBypassRule",
    "UrlPhishingShortenerRule",
    "BurnerMuleSimRule",
]
