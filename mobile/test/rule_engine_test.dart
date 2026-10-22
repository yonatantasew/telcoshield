import 'package:flutter_test/flutter_test.dart';
import 'package:telcoshield_guard/engine/models.dart';
import 'package:telcoshield_guard/engine/telcoshield_rule_engine.dart';

void main() {
  group('TelcoShieldRuleEngine On-Device Mobile Tests', () {
    test('CASE 1: Legitimate Telebirr SMS should be ALLOWED', () {
      final report = TelcoShieldRuleEngine.inspect(
        senderId: 'telebirr',
        messageBody: 'Your telebirr account has been credited with 3,500 ETB. Ref: TX884192.',
      );

      expect(report.verdict, equals(Verdict.allowed));
      expect(report.isFraud, isFalse);
      expect(report.violations, isEmpty);
    });

    test('CASE 2: Legitimate Shortcode 127 should be ALLOWED', () {
      final report = TelcoShieldRuleEngine.inspect(
        senderId: '127',
        messageBody: 'የቴሌብር ሂሳብዎ በ 45,000 ብር ተሞልቷል። ቀሪ ሂሳብ 52,100 ብር።',
      );

      expect(report.verdict, equals(Verdict.allowed));
      expect(report.isFraud, isFalse);
    });

    test('CASE 3: Fake Telebirr Receipt from Personal Phone should be BLOCKED_FRAUD', () {
      final report = TelcoShieldRuleEngine.inspect(
        senderId: '+251933445566',
        messageBody: 'Your telebirr account has been credited with 45,000 ETB from CBE Birr. Ref: TX998123.',
      );

      expect(report.verdict, equals(Verdict.blockedFraud));
      expect(report.severity, equals(ThreatSeverity.critical));
      expect(report.isFraud, isTrue);
      expect(report.violations.any((v) => v.ruleCode == 'RULE-META-001'), isTrue);
    });

    test('CASE 4: Amharic Fake Telebirr from Personal Phone should be BLOCKED_FRAUD', () {
      final report = TelcoShieldRuleEngine.inspect(
        senderId: '+251912345678',
        messageBody: 'የቴሌብር ሂሳብዎ በ 45,000 ብር ተሞልቷል። ቀሪ ሂሳብ 52,100 ብር። የግብይት ቁጥር: TX998123።',
      );

      expect(report.verdict, equals(Verdict.blockedFraud));
      expect(report.severity, equals(ThreatSeverity.critical));
      expect(report.isFraud, isTrue);
      expect(report.violations.first.ruleCode, equals('RULE-META-001'));
    });

    test('CASE 5: Fayda OTP Harvesting scam should be BLOCKED_FRAUD', () {
      final report = TelcoShieldRuleEngine.inspect(
        senderId: '+251922334455',
        messageBody: 'Telebirr Alert: Link your account to Fayda National ID immediately. Your verification code OTP is 778129.',
      );

      expect(report.verdict, equals(Verdict.blockedFraud));
      expect(report.isFraud, isTrue);
      expect(report.violations.any((v) => v.ruleCode == 'RULE-META-002'), isTrue);
    });

    test('CASE 6: Weaponized URL shortener should be BLOCKED_FRAUD', () {
      final report = TelcoShieldRuleEngine.inspect(
        senderId: '+251955667788',
        messageBody: 'Update your bank KYC now to avoid suspension: https://bit.ly/telebirr-kyc-verify',
      );

      expect(report.verdict, equals(Verdict.blockedFraud));
      expect(report.violations.any((v) => v.ruleCode == 'RULE-URL-001'), isTrue);
    });
  });
}
