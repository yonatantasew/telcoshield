"""
TelcoShield Automated Benchmark Suite
Evaluates PAiCore OpenTextShield Baseline against TelcoShield Hybrid Engine.
"""

from telcoshield import TelcoShieldEngine, MessageContext, IngressRoute, Verdict


def run_benchmark():
    engine = TelcoShieldEngine()

    test_scenarios = [
        {
            "id": "CASE-1: Normal Interpersonal SMS",
            "ctx": MessageContext(
                sender_id="+251911223344",
                text="Hey Abebe, I will meet you at the cafe around 4 PM.",
                ingress_route=IngressRoute.DOMESTIC_ONNET
            ),
            "expected_verdict": Verdict.ALLOWED
        },
        {
            "id": "CASE-2: Global Phishing (Netflix Scam)",
            "ctx": MessageContext(
                sender_id="+447123456789",
                text="Your Netflix subscription has expired. Update billing now at http://bit.ly/netflix-renew-2026 or service will be cut.",
                ingress_route=IngressRoute.INTERNATIONAL_IPX
            ),
            "expected_verdict": Verdict.BLOCKED_FRAUD
        },
        {
            "id": "CASE-3: Oct 17 Police Raid Pretext (Fayda OTP Theft)",
            "ctx": MessageContext(
                sender_id="+251922334455",
                text="Telebirr Alert: Your account must be linked to Fayda Digital ID within 24 hours to prevent account freeze. Call 0911XXXXXX or share your OTP code with support.",
                ingress_route=IngressRoute.DOMESTIC_ONNET
            ),
            "expected_verdict": Verdict.BLOCKED_FRAUD
        },
        {
            "id": "CASE-4A: FAKE Telebirr Merchant Receipt (Merkato Scam)",
            "ctx": MessageContext(
                sender_id="+251933445566",  # FRAUDSTER'S PERSONAL SIM!
                text="Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.",
                ingress_route=IngressRoute.DOMESTIC_ONNET
            ),
            "expected_verdict": Verdict.BLOCKED_FRAUD
        },
        {
            "id": "CASE-4B: LEGITIMATE Telebirr Merchant Receipt (Control)",
            "ctx": MessageContext(
                sender_id="telebirr",  # OFFICIAL AUTHORIZED SHORTCODE!
                text="Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.",
                ingress_route=IngressRoute.DOMESTIC_ONNET
            ),
            "expected_verdict": Verdict.ALLOWED
        },
        {
            "id": "CASE-6: A2P Grey Route Interconnect Bypass",
            "ctx": MessageContext(
                sender_id="telebirr",
                text="Your telebirr account has been credited with 10,000 ETB.",
                ingress_route=IngressRoute.INTERNATIONAL_IPX,  # Arriving from foreign link!
                calling_gt="+447900000000"
            ),
            "expected_verdict": Verdict.BLOCKED_FRAUD
        },
        {
            "id": "CASE-7: Burner / Mule SIM Burst Activity",
            "ctx": MessageContext(
                sender_id="+251955667788",
                text="Urgent: Payment of 8,500 ETB sent for goods. Please confirm receipt and release package.",
                sim_age_hours=2.0  # Freshly activated (<24h)
            ),
            "expected_verdict": Verdict.BLOCKED_FRAUD
        }
    ]

    print("=" * 80)
    print("TELCOSHIELD HYBRID SECURITY BENCHMARK REPORT")
    print("PAiCore OpenTextShield mBERT (v2.9) + Carrier Signaling Rules")
    print("=" * 80)

    for case in test_scenarios:
        report = engine.inspect(case["ctx"])
        
        print(f"\n[{case['id']}]")
        print(f"  Sender ID:            {case['ctx'].sender_id} ({case['ctx'].ingress_route.value})")
        print(f"  PAiCore mBERT NLP:    {report.nlp_result.label.upper()} ({report.nlp_result.confidence*100:.1f}%)")
        print(f"  TelcoShield Verdict:  {report.verdict.value} (Risk: {report.risk_score*100:.0f}%, {report.threat_severity.value})")
        print(f"  Gateway Action:       {report.gateway_action}")
        print(f"  Metadata Override?:   {'YES [FLIPPED RAW NLP FALSE NEGATIVE!]' if report.metadata_override else 'No'}")
        print(f"  Latency:              {report.total_latency_ms:.1f} ms (mBERT: {report.nlp_result.processing_time_ms:.1f} ms)")
        if report.violations:
            print("  Triggered Rules:")
            for v in report.violations:
                print(f"    -> [{v.rule_id}] {v.title}: {v.description}")

        assert report.verdict == case["expected_verdict"], f"Failed on {case['id']}"

    print("\n" + "=" * 80)
    print("ALL 7 SCENARIOS PASSED WITH 100% SPECIFICATION ACCURACY!")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
