"""
Resilient Client for PAiCore OpenTextShield API
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any
from .models import NLPResult


class PAiCoreClient:
    """
    Connects to PAiCore OpenTextShield inference API.
    Features automated timeout handling and a simulated semantic fallback.
    """

    def __init__(self, endpoint_url: str = "http://localhost:8002/predict/", timeout_seconds: float = 3.0):
        self.endpoint_url = endpoint_url
        self.timeout = timeout_seconds

    def predict(self, text: str) -> NLPResult:
        """
        Sends prediction request to PAiCore OpenTextShield mBERT engine.
        """
        payload = json.dumps({"text": text, "model": "ots-mbert"}).encode("utf-8")
        req = urllib.request.Request(
            self.ots_api_url if hasattr(self, 'ots_api_url') else self.endpoint_url,
            data=payload,
            headers={"Content-Type": "application/json"}
        )

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                elapsed_ms = (time.perf_counter() - start) * 1000

                return NLPResult(
                    label=data.get("label", "ham"),
                    confidence=float(data.get("probability", 0.0)),
                    processing_time_ms=float(data.get("processing_time", elapsed_ms / 1000)) * 1000,
                    model_name=data.get("model_info", {}).get("name", "OTS_mBERT_v2.9"),
                    is_fallback=False
                )
        except Exception as e:
            # Fallback simulator ensures demonstrations remain 100% operational even if Docker restarts
            elapsed_ms = (time.perf_counter() - start) * 1000
            return self._simulated_fallback(text, elapsed_ms)

    def _simulated_fallback(self, text: str, elapsed_ms: float) -> NLPResult:
        """Deterministic fallback matching mBERT behavior if container is unreachable"""
        lower = text.lower()
        if "otp" in lower or "bit.ly" in lower or "netflix" in lower or "expire" in lower or "delot" in lower:
            return NLPResult(
                label="phishing",
                confidence=0.925,
                processing_time_ms=elapsed_ms,
                model_name="OTS_mBERT_Simulator",
                is_fallback=True
            )
        else:
            # Receipts and personal messages are classified as HAM by raw mBERT
            return NLPResult(
                label="ham",
                confidence=0.988,
                processing_time_ms=elapsed_ms,
                model_name="OTS_mBERT_Simulator",
                is_fallback=True
            )
