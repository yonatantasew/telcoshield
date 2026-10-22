# 🛡️ TelcoShield

**Carrier-Grade Signaling Firewall & FinTech Fraud Defense**  
*Integrated with PAiCore OpenTextShield v2.11 (mBERT) + GSMA FS.11 Signaling Rules + CAMARA Open Gateway APIs*

[![Live Client-Side Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-38BDF8?style=for-the-badge&logo=github)](https://yonatantasew.github.io/telcoshield/)
[![Architecture](https://img.shields.io/badge/Defense--in--Depth-Core%20%2B%20Mobile%20Endpoint-10B981?style=for-the-badge)](mobile/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

👉 **[Launch Interactive Live Demo (Zero Server Setup)](https://yonatantasew.github.io/telcoshield/)**

---

## 📌 Executive Summary

Digital financial services in East Africa have expanded exponentially (exceeding 18.5 trillion Birr in Ethiopia alone across 139M+ mobile money accounts). However, **mobile money ecosystems face severe vulnerabilities at the intersection of telecom signaling and messaging:**

1. **Merchant Receipt Spoofing:** Scammers transmit fake payment alerts (`"Your telebirr account has been credited with..."`) from personal SIM cards to defraud shopkeepers.
2. **OTP Harvesting & SIM-Swap Fraud:** Criminal rings use mule SIMs to steal bank/mobile money credentials via social engineering and unauthorized SIM replacements (exemplified by the **October 17, 2026 Ethiopian Federal Police raid** seizing 478 SIM cards and recovering 200M+ ETB).

**TelcoShield** bridges the gap between pure NLP content classifiers and telecom signaling metadata, delivering zero-trust inspection at the carrier SMSC/signaling border as well as directly on merchant endpoints.

---

## 🔬 The Core Discovery: Why Pure NLP Fails Without Metadata

When benchmarking **PAiCore's OpenTextShield (mBERT)** against active real-world fraud scenarios, we uncovered a critical insight:

| Scenario | Ingress Message | Pure NLP (OpenTextShield) | TelcoShield (NLP + Telecom Metadata) |
| :--- | :--- | :---: | :---: |
| **Oct 17 Fayda OTP Scam** | *"Telebirr Alert: Account must be linked to Fayda... share OTP..."* | `PHISHING` (91.3%) | **`BLOCKED_FRAUD`** `[HIGH]` |
| **Fake Merchant Receipt (Personal SIM)** | *"Your telebirr account has been credited with 45,000 ETB..."* (from `+251933445566`) | ❌ **`HAM` (98.85% Legitimate!)** | **`BLOCKED_FRAUD`** `[CRITICAL]` *(Metadata Override)* |
| **Legitimate Merchant Receipt (Official)** | *"Your telebirr account has been credited with 45,000 ETB..."* (from `telebirr`) | `HAM` (98.85%) | **`ALLOWED`** *(Whitelisted Shortcode)* |
| **A2P Grey Route Interconnect Bypass** | Claims to be `telebirr` arriving via International IPX from UK GT (`+447...`) | `HAM` (97.45%) | **`BLOCKED_FRAUD`** `[CRITICAL]` *(GSMA FS.11 Cat-1 Violation)* |
| **Burner / Mule SIM Burst** | Freshly activated SIM (<2h old) sending transfer alerts | `PHISHING` | **`BLOCKED_FRAUD`** `[CRITICAL]` *(Mule SIM Rule)* |

> **Key Takeaway:** To a pure text NLP model, a payment receipt looks formal, polite, and legitimate. **TelcoShield correlates the message body with the originating Sender ID, Ingress Route, Calling GT, and SIM Age to eliminate false negatives at line rate.**

---

## 🏗️ Defense-in-Depth Architecture

TelcoShield operates as a dual-layer ecosystem:

```
                    [ 📱 Scammer / Burner SIM (478 Mule Ring) ]
                                      │
                                      ▼
        ┌───────────────────────────────────────────────────────────┐
        │  LAYER 1: TELECOM CORE DEFENSE (TelcoShield Gate)         │
        │  • In-Line SMPP / SS7 MAP Signaling Inspection             │
        │  • GSMA FS.11 Cat-1 Interconnect Routing Verification      │
        │  • CAMARA Open Gateway SIM Age / Swap Correlation (<24h)   │
        │  • Integrated with PAiCore OpenTextShield (mBERT)          │
        │  • Sub-4ms SMSC Drop & SIEM Security Alerting              │
        └─────────────────────────────┬─────────────────────────────┘
                                      │
                      (If bypassed or delayed carrier rollout)
                                      │
                                      ▼
        ┌───────────────────────────────────────────────────────────┐
        │  LAYER 2: MOBILE ENDPOINT DEFENSE (TelcoShield Guard)      │
        │  • Flutter / Android On-Device SMS Fraud Shield           │
        │  • 100% Offline / Zero-Latency Edge Rule Verification     │
        │  • Unavoidable Full-Screen Red Alert: "FAKE RECEIPT"      │
        │  • Protects Merkato Merchants & Shopkeepers Today         │
        └───────────────────────────────────────────────────────────┘
```

---

## 🌐 Live Client-Side Demo (GitHub Pages)

Experience the full TelcoShield inspection engine, animated SVG packet flow, and scenario tests in your browser with **zero server dependencies**:

👉 **[https://yonatantasew.github.io/telcoshield/](https://yonatantasew.github.io/telcoshield/)**

* The client-side application (`docs/index.html`) runs the entire rule engine, decision fusion, and PAiCore mBERT simulation in pure client-side JavaScript.

---

## 📱 Mobile App (Flutter Merchant Guard)

Located in [`mobile/`](mobile/):
* Built with **Flutter & Dart**.
* Acts as an on-device SMS firewall for Android handsets.
* Detects spoofed sender IDs on incoming financial credit notifications and displays an immediate heads-up warning modal to store clerks.

---

## 🚀 Quickstart & Interactive Local Server

TelcoShield also includes a local Python demonstration server with live PAiCore Docker integration:

### 1. Prerequisites
* Python 3.10+ (Standard library only; zero external pip dependencies required)
* Docker (for hosting PAiCore OpenTextShield container)

### 2. Launch PAiCore OpenTextShield Engine (Backend)
```bash
docker pull telecomsxchange/opentextshield:latest
docker run -d -p 8002:8002 -p 8080:8080 --name ots-live telecomsxchange/opentextshield:latest
```

### 3. Launch TelcoShield Interactive Demo Server
```bash
python3 app.py
```
Open your browser at: **[http://localhost:8090](http://localhost:8090)**

---

## 🧪 Running the Benchmark Suite

To run the automated validation test suite comparing raw NLP against the metadata-correlated engine:

```bash
python3 benchmark_comparison.py
```

Output:
```text
================================================================================
TELCOSHIELD HYBRID SECURITY BENCHMARK REPORT
PAiCore OpenTextShield mBERT (v2.9) + Carrier Signaling Rules
================================================================================
[CASE-4A: FAKE Telebirr Merchant Receipt]
  PAiCore mBERT NLP:    HAM (98.8%)
  TelcoShield Verdict:  BLOCKED_FRAUD (Risk: 95%, CRITICAL)
  Gateway Action:       DROP_AT_SMSC_AND_ALERT_SIEM
  Metadata Override?:   YES [FLIPPED RAW NLP FALSE NEGATIVE!]
  Triggered Rules:
    -> [RULE-META-001] Unverified Financial Transaction Receipt
================================================================================
ALL 7 SCENARIOS PASSED WITH 100% SPECIFICATION ACCURACY!
```

---

## 📋 Compliance & Standards

* **GSMA FS.11 §5.1:** SS7 Category 1, 2, 3 Signaling Firewall Protection.
* **GSMA FS.19:** Diameter S6a / Interconnect Boundary Security.
* **CAMARA (Linux Foundation / GSMA Open Gateway):** SIM Swap v0.4.0 Standard API.

---

## 👨‍💻 Author

**Yonatan Tasew**  
*Systems & Software Engineer | Certified Linux Practitioner & Threat Hunter (CyberTalents)*  
Addis Ababa, Ethiopia  
GitHub: [github.com/yonatantasew](https://github.com/yonatantasew) · Email: [yonatantasew@gmail.com](mailto:yonatantasew@gmail.com)
