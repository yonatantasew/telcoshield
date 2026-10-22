import 'package:flutter/material.dart';
import 'engine/models.dart';
import 'engine/telcoshield_rule_engine.dart';
import 'widgets/fraud_alert_dialog.dart';

void main() {
  runApp(const TelcoShieldGuardApp());
}

class TelcoShieldGuardApp extends StatelessWidget {
  const TelcoShieldGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TelcoShield Merchant Guard',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0B0F19),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF38BDF8),
          surface: Color(0xFF1E293B),
        ),
        fontFamily: 'Roboto',
      ),
      home: const DashboardScreen(),
    );
  }
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final List<InspectionReport> _history = [];
  int _blockedCount = 0;
  int _verifiedCount = 0;

  final TextEditingController _senderController = TextEditingController(text: '+251933445566');
  final TextEditingController _bodyController = TextEditingController(
    text: 'Your telebirr account has been credited with 45,000 ETB from CBE Birr. Ref: TX998123.',
  );

  @override
  void initState() {
    super.initState();
    _loadSampleEvents();
  }

  void _loadSampleEvents() {
    _inspectMessage(
      senderId: 'telebirr',
      body: 'Your telebirr account has been credited with 3,500 ETB from Abebe Kebede. Ref: TX884192.',
      silent: true,
    );
    _inspectMessage(
      senderId: '+251933445566',
      body: 'Your telebirr account has been credited with 45,000 ETB from CBE Birr. Ref: TX998123.',
      silent: true,
    );
  }

  void _inspectMessage({
    required String senderId,
    required String body,
    bool silent = false,
  }) {
    final report = TelcoShieldRuleEngine.inspect(
      senderId: senderId,
      messageBody: body,
    );

    setState(() {
      _history.insert(0, report);
      if (report.isFraud) {
        _blockedCount++;
      } else {
        _verifiedCount++;
      }
    });

    if (!silent && report.isFraud) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => FraudAlertDialog(
          report: report,
          onDismiss: () => Navigator.of(ctx).pop(),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFF0284C7).withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.shield, color: Color(0xFF38BDF8), size: 20),
            ),
            const SizedBox(width: 10),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'TelcoShield Guard',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  'On-Device Merchant Defense',
                  style: TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                ),
              ],
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF10B981).withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
              border: Border.Border.all(color: const Color(0xFF10B981).withOpacity(0.3)),
            ),
            child: const Row(
              children: [
                Icon(Icons.check_circle, color: Color(0xFF10B981), size: 12),
                SizedBox(width: 4),
                Text(
                  'ACTIVE',
                  style: TextStyle(
                    color: Color(0xFF10B981),
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // KPI Stat Cards
            Row(
              children: [
                Expanded(
                  child: _buildKpiCard(
                    title: 'SCAMS BLOCKED',
                    count: '$_blockedCount',
                    color: const Color(0xFFEF4444),
                    icon: Icons.block,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildKpiCard(
                    title: 'LEGIT RECEIPTS',
                    count: '$_verifiedCount',
                    color: const Color(0xFF10B981),
                    icon: Icons.verified_user_outlined,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Live Simulator / Test Box
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.Border.all(color: Colors.white10),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'TEST INCOMING SMS (ON-DEVICE SIMULATOR)',
                    style: TextStyle(
                      color: Color(0xFF94A3B8),
                      fontSize: 11,
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _senderController,
                    decoration: InputDecoration(
                      labelText: 'Sender Address (MSISDN / Shortcode)',
                      labelStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                      filled: true,
                      fillColor: const Color(0xFF0F172A),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: _bodyController,
                    maxLines: 2,
                    decoration: InputDecoration(
                      labelText: 'SMS Content / Payment Receipt',
                      labelStyle: const TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                      filled: true,
                      fillColor: const Color(0xFF0F172A),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            _senderController.text = 'telebirr';
                            _bodyController.text =
                                'Your telebirr account has been credited with 2,000 ETB. Ref: TX776192.';
                          },
                          child: const Text('Preset: Legit Telebirr', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () {
                            _senderController.text = '+251933445566';
                            _bodyController.text =
                                'Your telebirr account has been credited with 45,000 ETB from CBE Birr. Ref: TX998123.';
                          },
                          child: const Text('Preset: Fake Receipt', style: TextStyle(fontSize: 11)),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0284C7),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      icon: const Icon(Icons.flash_on, size: 18),
                      label: const Text('Simulate Incoming SMS Intercept'),
                      onPressed: () {
                        _inspectMessage(
                          senderId: _senderController.text,
                          body: _bodyController.text,
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Intercept History Feed
            const Text(
              'LIVE ON-DEVICE INSPECTION FEED',
              style: TextStyle(
                color: Color(0xFF94A3B8),
                fontSize: 11,
                fontFamily: 'monospace',
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 10),
            ..._history.map((report) => _buildHistoryItem(report)),
          ],
        ),
      ),
    );
  }

  Widget _buildKpiCard({
    required String title,
    required String count,
    required Color color,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
        border: Border.Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 10,
                  fontFamily: 'monospace',
                  fontWeight: FontWeight.bold,
                ),
              ),
              Icon(icon, color: color, size: 18),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            count,
            style: TextStyle(
              color: color,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryItem(InspectionReport report) {
    final bool isFraud = report.isFraud;
    final color = isFraud ? const Color(0xFFEF4444) : const Color(0xFF10B981);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF131C2E),
        borderRadius: BorderRadius.circular(12),
        border: Border.Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(
                    isFraud ? Icons.cancel_outlined : Icons.check_circle_outline,
                    color: color,
                    size: 16,
                  ),
                  const SizedBox(width: 6),
                  Text(
                    isFraud ? 'BLOCKED FRAUD' : 'VERIFIED LEGITIMATE',
                    style: TextStyle(
                      color: color,
                      fontSize: 11,
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              Text(
                'Sender: ${report.senderId}',
                style: const TextStyle(
                  color: Color(0xFF94A3B8),
                  fontFamily: 'monospace',
                  fontSize: 11,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            report.messageBody,
            style: const TextStyle(color: Colors.white, fontSize: 13),
          ),
          if (isFraud) ...[
            const SizedBox(height: 8),
            Text(
              report.violations.first.description,
              style: const TextStyle(color: Color(0xFFFCA5A5), fontSize: 11),
            ),
          ],
        ],
      ),
    );
  }
}
