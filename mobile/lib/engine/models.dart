enum Verdict {
  allowed,
  flaggedSuspicious,
  blockedFraud,
}

enum ThreatSeverity {
  info,
  medium,
  high,
  critical,
}

class RuleViolation {
  final String ruleCode;
  final ThreatSeverity severity;
  final String title;
  final String description;

  RuleViolation({
    required this.ruleCode,
    required this.severity,
    required this.title,
    required this.description,
  });
}

class InspectionReport {
  final String senderId;
  final String messageBody;
  final Verdict verdict;
  final ThreatSeverity severity;
  final double riskScore;
  final List<RuleViolation> violations;
  final bool isFraud;
  final DateTime timestamp;

  InspectionReport({
    required this.senderId,
    required this.messageBody,
    required this.verdict,
    required this.severity,
    required this.riskScore,
    required this.violations,
    required this.isFraud,
    required this.timestamp,
  });
}
