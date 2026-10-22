import 'models.dart';

/// On-Device Carrier-Grade SMS Fraud Inspection Engine (Dart / Flutter)
/// Evaluates incoming SMS in <1ms without requiring external internet or API access.
class TelcoShieldRuleEngine {
  static final List<String> brandWhitelist = [
    'telebirr',
    'cbebirr',
    'cbe',
    'mpesa',
    'm-pesa',
    'awashbank',
    'bankofabyssinia',
  ];

  static final List<String> financialBrands = [
    'telebirr',
    'cbe birr',
    'cbebirr',
    'commercial bank of ethiopia',
    'm-pesa',
    'mpesa',
    'awash birr',
    'awashbirr',
    'boa',
    'abyssinia',
  ];

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
  ];

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
  ];

  static final List<String> authKeywords = [
    'otp',
    'verification code',
    'pin',
    'password',
    'do not share',
    'your code is',
    'one-time password',
    'security code',
  ];

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
        title: 'Fake Financial Transaction Receipt',
        description: 'Message claims an official payment or credit receipt, but originates from a personal phone number ($senderTrimmed) rather than the official verified carrier shortcode.',
      ));
    }

    // Rule 2: Credential Harvesting / OTP Phishing (RULE-META-002)
    final bool hasAuthBrand = authBrands.any((b) => textLower.contains(b));
    final bool hasAuthKW = authKeywords.any((k) => textLower.contains(k));

    if (hasAuthBrand && hasAuthKW && !isWhitelisted) {
      violations.add(RuleViolation(
        ruleCode: 'RULE-META-002',
        severity: ThreatSeverity.critical,
        title: 'Unauthorized OTP / Credential Request',
        description: 'Message requests sensitive verification codes (OTP/PIN/Fayda) from an unverified personal sender ($senderTrimmed).',
      ));
    }

    // Rule 3: Suspicious Phishing URL Shorteners (RULE-URL-001)
    final bool hasShortener = urlShorteners.any((u) => textLower.contains(u));
    if (hasShortener) {
      violations.add(RuleViolation(
        ruleCode: 'RULE-URL-001',
        severity: ThreatSeverity.high,
        title: 'Suspicious / Weaponized URL Shortener',
        description: 'Message contains an unverified URL or link shortener known to circumvent basic spam filters.',
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
