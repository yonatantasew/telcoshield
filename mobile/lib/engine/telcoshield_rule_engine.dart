import 'models.dart';

/// On-Device Carrier-Grade SMS Fraud Inspection Engine (Dart / Flutter)
/// Evaluates incoming SMS in <1ms without requiring external internet or API access.
/// Supports both English and Amharic (ግዕዝ) payment receipts.
class TelcoShieldRuleEngine {
  // Official carrier-whitelisted sender IDs and authorized SMS shortcodes
  static final List<String> brandWhitelist = [
    'telebirr',
    '127',               // Official Ethio Telecom Telebirr Shortcode
    'cbebirr',
    'cbe',
    '889',               // Official Commercial Bank of Ethiopia Shortcode
    'mpesa',
    'm-pesa',
    '707',               // Official Safaricom M-PESA Shortcode
    'awashbank',
    'awashbirr',
    '8989',              // Official Awash Bank Shortcode
    'bankofabyssinia',
    'boa',
    '811',               // Official Bank of Abyssinia Shortcode
    'dashenbank',
    'amole',
  ];

  // Financial brand triggers (English & Amharic / ግዕዝ)
  static final List<String> financialBrands = [
    'telebirr',
    'cbe birr',
    'cbebirr',
    'commercial bank of ethiopia',
    'm-pesa',
    'mpesa',
    'awash birr',
    'awashbank',
    'boa',
    'abyssinia',
    'dashen',
    'amole',
    // Amharic script
    'ቴሌብር',
    'ቴሌ ብር',
    'ሲቢኢ',
    'የኢትዮጵያ ንግድ ባንክ',
    'ኤምፔሳ',
    'አዋሽ ባንክ',
    'አቢሲኒያ',
    'ዳሽን',
  ];

  // Credential & identity harvesting triggers (English & Amharic)
  static final List<String> authBrands = [
    'telebirr',
    'cbe birr',
    'cbebirr',
    'm-pesa',
    'mpesa',
    'fayda',
    'national id',
    'nid',
    'bank',
    // Amharic script
    'ፋይዳ',
    'ብሔራዊ መታወቂያ',
    'ባንክ',
  ];

  // Financial transaction receipt keywords (English & Amharic)
  static final List<String> financialKeywords = [
    'credited with',
    'debited',
    'transfer of',
    'transferred',
    'received',
    'payment of',
    'account balance',
    'etb',
    'birr',
    'ref:',
    'tx:',
    'transaction id',
    // Amharic script
    'ተሞልቷል',
    'ተቀብለዋል',
    'ተላልፏል',
    'ተቆርጧል',
    'ብር',
    'ሂሳብ',
    'ቀሪ ሂሳብ',
    'የግብይት ቁጥር',
    'የትራንዛክሽን ቁጥር',
  ];

  // Authentication & OTP keywords (English & Amharic)
  static final List<String> authKeywords = [
    'otp',
    'verification code',
    'pin',
    'password',
    'do not share',
    'your code is',
    'one-time password',
    'security code',
    // Amharic script
    'የይለፍ ቃል',
    'የማረጋገጫ ኮድ',
    'ኦቲፒ',
    'ለማንም አያጋሩ',
    'ኮድዎ',
  ];

  // Weaponized URL shorteners & lookalike domains
  static final List<String> urlShorteners = [
    'bit.ly',
    'tinyurl.com',
    't.co',
    'is.gd',
    'cutt.ly',
    'ngrok.io',
    'telebirr.me',
    'telebirr-et.com',
    'cbe-et.com',
    'fayda-verify.com',
  ];

  /// Inspect an incoming SMS message synchronously on-device in <1ms
  static InspectionReport inspect({
    required String senderId,
    required String messageBody,
  }) {
    final senderTrimmed = senderId.trim();
    final senderLower = senderTrimmed.toLowerCase();
    final textLower = messageBody.toLowerCase();

    final List<RuleViolation> violations = [];
    final bool isWhitelisted = brandWhitelist.contains(senderLower);

    // Rule 1: Financial Brand Impersonation (RULE-META-001)
    final bool hasFinancialBrand = financialBrands.any((b) => textLower.contains(b));
    final bool hasFinancialKW = financialKeywords.any((k) => textLower.contains(k));

    if (hasFinancialBrand && hasFinancialKW && !isWhitelisted) {
      violations.add(RuleViolation(
        ruleCode: 'RULE-META-001',
        severity: ThreatSeverity.critical,
        title: 'Fake Financial Transaction Receipt / የሀሰት ክፍያ ደረሰኝ',
        description: 'Message claims an official financial payment/credit, but originates from an unverified phone number ($senderTrimmed) rather than official carrier shortcodes (127, 889, telebirr, CBEBirr).',
      ));
    }

    // Rule 2: Credential Harvesting / OTP Phishing (RULE-META-002)
    final bool hasAuthBrand = authBrands.any((b) => textLower.contains(b));
    final bool hasAuthKW = authKeywords.any((k) => textLower.contains(k));

    if (hasAuthBrand && hasAuthKW && !isWhitelisted) {
      violations.add(RuleViolation(
        ruleCode: 'RULE-META-002',
        severity: ThreatSeverity.critical,
        title: 'Unauthorized OTP / Credential Harvesting',
        description: 'Message requests sensitive verification codes (OTP/PIN/Fayda) from an unauthorized personal sender ($senderTrimmed).',
      ));
    }

    // Rule 3: Suspicious Phishing URL Shorteners (RULE-URL-001)
    final bool hasShortener = urlShorteners.any((u) => textLower.contains(u));
    if (hasShortener) {
      violations.add(RuleViolation(
        ruleCode: 'RULE-URL-001',
        severity: ThreatSeverity.high,
        title: 'Suspicious / Weaponized URL Shortener',
        description: 'Message contains an unverified URL shortener known to circumvent basic spam filters.',
      ));
    }

    final bool isFraud = violations.isNotEmpty;
    final Verdict verdict = isFraud ? Verdict.blockedFraud : Verdict.allowed;
    final ThreatSeverity severity = isFraud
        ? (violations.any((v) => v.severity == ThreatSeverity.critical)
            ? ThreatSeverity.critical
            : ThreatSeverity.high)
        : ThreatSeverity.info;
    final double riskScore = isFraud ? 0.95 : 0.05;

    return InspectionReport(
      senderId: senderTrimmed,
      messageBody: messageBody,
      verdict: verdict,
      severity: severity,
      riskScore: riskScore,
      violations: violations,
      isFraud: isFraud,
      timestamp: DateTime.now(),
    );
  }
}
