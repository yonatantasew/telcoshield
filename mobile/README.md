# 📱 TelcoShield Merchant Guard (On-Device Mobile Client)

**Real-Time On-Device SMS Fraud Defense & Payment Receipt Verification for Merchants**

Built with **Flutter & Dart**, TelcoShield Guard serves as the **Endpoint Protection Layer** in TelcoShield's Defense-in-Depth architecture. While the TelcoShield Gateway protects the telecom core at the SMSC/SMPP level, this mobile app empowers Ethiopian merchants, shopkeepers, and kiosk operators to protect themselves on their own smartphones today.

---

## 🎯 The Real-World Problem It Solves

During the recent **October 2026 Ethiopian Federal Police raids**, investigators seized **478 mule SIM cards** used in an organized fraud ring that stole over **200M+ ETB**. 

A primary attack vector in open markets (Merkato, Piassa, Bole) involves scammers purchasing goods and sending a fake SMS confirmation from a personal SIM card (`+2519...`):
> *"Your telebirr account has been credited with 45,000 ETB from CBE Birr. Ref: TX998123."*

Because merchants are busy and the text looks identical to genuine Telebirr or CBE receipts, goods are handed over before the merchant realizes their bank balance never increased.

---

## 🛡️ How TelcoShield Guard Works (On-Device)

1. **Sub-1ms Synchronous Inspection**: Operates completely offline on the phone without querying external cloud servers or sharing sensitive user SMS data.
2. **Authority Mismatch Detection (`RULE-META-001`)**:
   - If incoming SMS contains financial receipt keywords (`credited with`, `payment of`, `transfer of`, `ETB`, `Ref:`) claiming to be Telebirr, CBE, or M-Pesa...
   - BUT the originating sender address is a standard phone number (`+2519...`) rather than the verified carrier alphanumeric shortcode (`telebirr`, `cbebirr`)...
   - The app instantly intercepts it as **CRITICAL FRAUD**.
3. **High-Urgency Alert Modal**: Displays an unavoidable, full-screen red warning modal:
   - **`⚠️ FAKE PAYMENT RECEIPT DETECTED`**
   - **`DO NOT RELEASE GOODS OR CASH`**
   - Displays the scammer's real phone number to assist police reporting.

---

## 🏗️ Architecture: Defense-in-Depth

```
                 [ 📱 Scammer / Burner SIM ]
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │  NETWORK CORE DEFENSE (TelcoShield Gate) │
        │  • SMPP/SS7 Carrier Ingress Firewall    │
        │  • GSMA FS.11 Cat-1 Interconnect Check  │
        │  • CAMARA SIM Activation Age (<24h)     │
        │  • In-Line PAiCore mBERT Correlation     │
        └─────────────────────┬────────────────────┘
                              │
            (If bypassed or delayed network rollout)
                              │
                              ▼
        ┌──────────────────────────────────────────┐
        │  ENDPOINT DEFENSE (TelcoShield Guard)    │
        │  • Flutter / Android On-Device Receiver  │
        │  • 100% Offline / Zero-Latency Check    │
        │  • Heads-Up Red Merchant Alert Banner    │
        │  • Merchant & Store Inventory Protected   │
        └──────────────────────────────────────────┘
```

---

## 🚀 Running the Flutter App

```bash
cd mobile
flutter pub get
flutter run
```

### Android Permissions (Manifest)
```xml
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.READ_SMS" />
```
