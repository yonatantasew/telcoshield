"""
Base Rule Definition for TelcoShield Rule Engine
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models import MessageContext, NLPResult, RuleViolation


class BaseRule(ABC):
    """Abstract base class for all metadata & signaling security rules"""
    
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier (e.g., RULE-META-001, GSMA-FS11-001)"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for telemetry and dashboard reporting"""
        pass

    @abstractmethod
    def evaluate(self, ctx: MessageContext, nlp: NLPResult) -> Optional[RuleViolation]:
        """
        Evaluates the message context and NLP output.
        Returns a RuleViolation if an anomaly or violation is detected, else None.
        """
        pass
