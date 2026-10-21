"""
TelcoShield vs. Baseline PAiCore OpenTextShield Benchmark
Runs real-world test cases to demonstrate how the Metadata Adapter eliminates false negatives.
"""

import json
from adapter import TelcoShieldAdapter

def run_benchmark():
    adapter = TelcoShieldAdapter(ots_api_url="http://localhost:8002/predict/")

    test_scenarios = [
        {
            "id": "CASE-1: Normal Interpersonal SMS",
            "sender_id": "+251911223344",
            "text": "Hey Abebe, I will meet you at the cafe around 4 PM.",
            "expected_verdict": "ALLOWED"
        },
        {
            "id": "CASE-2: Global Phishing (Netflix Scam)",
            "sender_id": "+447123456789",
            "text": "Your Netflix subscription has expired. Update billing now at http://bit.ly/netflix-renew-2026 or service will be cut.",
            "expected_verdict": "BLOCKED_FRAUD"
        },
        {
            "id": "CASE-3: Oct 17 Police Raid Pretext (Fayda OTP Theft)",
            "sender_id": "+251922334455",  # Unauthorized mobile phone pretending to be support
            "text": "Telebirr Alert: Your account must be linked to Fayda Digital ID within 24 hours to prevent account freeze. Call 0911XXXXXX or share your OTP code with support.",
            "expected_verdict": "BLOCKED_FRAUD"
        },
        {
            "id": "CASE-4A: FAKE Telebirr Merchant Receipt (Merkato Scam)",
            "sender_id": "+251933445566",  # FRAUDSTER'S PHONE NUMBER!
            "text": "Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.",
            "expected_verdict": "BLOCKED_FRAUD"
        },
        {
            "id": "CASE-4B: LEGITIMATE Telebirr Merchant Receipt (Control Test)",
            "sender_id": "telebirr",  # OFFICIAL TELEBIRR SENDER ID!
            "text": "Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.",
            "expected_verdict": "ALLOWED"
        },
        {
            "id": "CASE-5: Transliterated Amharic Prize Phishing",
            "sender_id": "+251944556677",
            "text": "Enkwan des alot! telebirr lay ye 50,000 birr delot teleyetual. lemeqebel yemiketlewn link yikefetu http://bit.ly/telebirr-prize",
            "expected_verdict": "BLOCKED_FRAUD"
        }
    ]

    print("=" * 80)
    print("TELCOSHIELD ADAPTER BENCHMARK REPORT: PAiCore OTS v2.11 + SENDER ID METADATA")
    print("=" * 80)

    for case in test_scenarios:
        res = adapter.inspect_message(case["sender_id"], case["text"])
        
        print(f"\n[{case['id']}]")
        print(f"  Sender ID:             {case['sender_id']}")
        print(f"  Message Body:          {case['text']}")
        print(f"  PAiCore Raw NLP Label: {res.paicore_nlp_label} (Confidence: {res.paicore_nlp_confidence*100:.2f}%)")
        print(f"  TelcoShield Verdict:   {res.final_verdict} (Severity: {res.threat_severity})")
        print(f"  Metadata Override?:    {'YES (OVERRODE RAW NLP FALSE NEGATIVE!)' if res.metadata_override else 'No'}")
        print(f"  Processing Latency:    {res.total_latency_ms} ms (OTS engine: {res.paicore_processing_time*1000:.1f} ms)")
        if res.rule_triggers:
            print("  Triggered Rules:")
            for t in res.rule_triggers:
                print(f"    -> {t}")

        # Verification check
        assert res.final_verdict == case["expected_verdict"], f"Mismatch on {case['id']}: expected {case['expected_verdict']} got {res.final_verdict}"

    print("\n" + "=" * 80)
    print("ALL TEST SCENARIOS PASSED WITH 100% SPECIFICATION ACCURACY!")
    print("=" * 80)

if __name__ == "__main__":
    run_benchmark()
