import 'dart:async';
import '../engine/models.dart';
import '../engine/telcoshield_rule_engine.dart';

/// Service coordinating real-time background and foreground SMS interception.
/// Listens to incoming SMS broadcasts and evaluates them via TelcoShieldRuleEngine.
class SmsReceiverService {
  static final SmsReceiverService _instance = SmsReceiverService._internal();
  factory SmsReceiverService() => _instance;
  SmsReceiverService._internal();

  final _streamController = StreamController<InspectionReport>.broadcast();
  Stream<InspectionReport> get onSmsInspected => _streamController.stream;

  final List<InspectionReport> _inspectionHistory = [];
  List<InspectionReport> get history => List.unmodifiable(_inspectionHistory);

  bool _isShieldActive = true;
  bool get isShieldActive => _isShieldActive;

  void toggleShield(bool active) {
    _isShieldActive = active;
  }

  /// Entry point called by Android BroadcastReceiver or Foreground Listener
  InspectionReport processIncomingSms({
    required String senderAddress,
    required String body,
  }) {
    final report = TelcoShieldRuleEngine.inspect(
      senderId: senderAddress,
      messageBody: body,
    );

    _inspectionHistory.insert(0, report);
    _streamController.add(report);

    return report;
  }

  /// Formats an official police/carrier fraud report ready to copy or submit
  String generatePoliceReport(InspectionReport report) {
    final buffer = StringBuffer();
    buffer.writeln('========================================');
    buffer.writeln('ETHIOPIAN POLICE / CARRIER FRAUD REPORT');
    buffer.writeln('TelcoShield On-Device Merchant Incident');
    buffer.writeln('========================================');
    buffer.writeln('Incident Timestamp: ${report.timestamp.toIso8601String()}');
    buffer.writeln('Scammer Phone Number: ${report.senderId}');
    buffer.writeln('Targeted FinTech: Telebirr / CBEBirr Impersonation');
    buffer.writeln('Threat Severity: ${report.severity.name.toUpperCase()}');
    buffer.writeln('Confidence / Risk Score: ${(report.riskScore * 100).toStringAsFixed(1)}%');
    buffer.writeln('----------------------------------------');
    buffer.writeln('Intercepted SMS Body:');
    buffer.writeln('"${report.messageBody}"');
    buffer.writeln('----------------------------------------');
    buffer.writeln('Violations:');
    for (final v in report.violations) {
      buffer.writeln('- [${v.ruleCode}] ${v.title}: ${v.description}');
    }
    buffer.writeln('========================================');
    buffer.writeln('Action Taken: MERCHANDISE RELEASE HALTED');
    buffer.writeln('Carrier Action Recommended: Block MSISDN / Blacklist IMEI');
    return buffer.toString();
  }

  void dispose() {
    _streamController.close();
  }
}
