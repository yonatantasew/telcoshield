#!/usr/bin/env python3
"""
TelcoShield Interactive Demo Server (Minimalist / Clean Demo Edition)
Simple, high-impact presentation layout with collapsible Advanced Telecom Parameters.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone, timedelta
from adapter import TelcoShieldAdapter

adapter = TelcoShieldAdapter(ots_api_url="http://localhost:8002/predict/")

# Simulated Carrier HSS/HLR SIM-Swap database
MOCK_SIM_DATABASE = {
    "+251933445566": datetime.now(timezone.utc) - timedelta(hours=3),      # Swapped 3 hours ago
    "+251922334455": datetime.now(timezone.utc) - timedelta(hours=14),     # Swapped 14 hours ago
    "+251911223344": datetime.now(timezone.utc) - timedelta(days=210),     # Clean
}

HTML_CLEAN_UI = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TelcoShield Demo | PAiCore OpenTextShield + Telecom Edge</title>
  
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          }
        }
      }
    }
  </script>

  <style>
    body {
      background-color: #030712;
      background-image: 
        radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.05) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%);
      background-attachment: fixed;
    }
    .glass-card {
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.07);
    }
    .scenario-active {
      border-color: #38bdf8 !important;
      background: rgba(30, 41, 59, 0.8) !important;
    }
  </style>
</head>
<body class="text-slate-100 min-h-screen antialiased flex flex-col justify-between p-4 sm:p-6 lg:p-8">

  <div class="max-w-5xl mx-auto w-full">
    
    <!-- Top Header -->
    <header class="flex items-center justify-between pb-6 mb-6 border-b border-slate-800/80">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            TelcoShield <span class="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-sky-400 font-mono font-medium">Demo Mode</span>
          </h1>
          <p class="text-xs text-slate-400">PAiCore OpenTextShield + Telecom Edge Defense</p>
        </div>
      </div>

      <!-- Live Connection Pill -->
      <div class="flex items-center gap-2 px-3 py-1 rounded-full glass-card text-xs text-emerald-400 font-medium">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
        PAiCore OTS Engine Active
      </div>
    </header>

    <!-- 3 Essential Demo Scenarios -->
    <div class="mb-6">
      <div class="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2.5 font-mono">
        Select Scenario to Demonstrate:
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        
        <!-- Scenario 1: The Blind Spot (The Star of the Demo) -->
        <button onclick="pickScenario('case4a', this)" class="scenario-pill scenario-active text-left p-3.5 rounded-xl glass-card border transition-all duration-200 hover:border-slate-600">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              THE BLIND SPOT
            </span>
            <span class="text-xs text-slate-500 font-mono">#01</span>
          </div>
          <div class="text-sm font-semibold text-slate-200">Fake Telebirr Payment Receipt</div>
          <div class="text-xs text-slate-400 mt-0.5">Scam receipt sent from personal phone</div>
        </button>

        <!-- Scenario 2: Control (Legitimate) -->
        <button onclick="pickScenario('case4b', this)" class="scenario-pill text-left p-3.5 rounded-xl glass-card border transition-all duration-200 hover:border-slate-600">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
              LEGITIMATE
            </span>
            <span class="text-xs text-slate-500 font-mono">#02</span>
          </div>
          <div class="text-sm font-semibold text-slate-200">Real Telebirr Receipt</div>
          <div class="text-xs text-slate-400 mt-0.5">Sent from official verified shortcode</div>
        </button>

        <!-- Scenario 3: Fayda OTP Scam (Police Raid) -->
        <button onclick="pickScenario('case3', this)" class="scenario-pill text-left p-3.5 rounded-xl glass-card border transition-all duration-200 hover:border-slate-600">
          <div class="flex items-center justify-between mb-1">
            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
              OCT 17 POLICE RAID
            </span>
            <span class="text-xs text-slate-500 font-mono">#03</span>
          </div>
          <div class="text-sm font-semibold text-slate-200">Fayda ID OTP Harvesting</div>
          <div class="text-xs text-slate-400 mt-0.5">Social engineering phishing SMS</div>
        </button>

      </div>
    </div>

    <!-- Main Workspace: Simple 2-Card Layout -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      
      <!-- Input Card (5 Cols) -->
      <div class="lg:col-span-5 glass-card rounded-2xl p-5 space-y-4">
        
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1 font-mono">SENDER ID (WHO SENT IT?)</label>
          <input type="text" id="senderInput" value="+251933445566"
            class="w-full bg-slate-950/80 border border-slate-800 focus:border-sky-500 rounded-xl px-3.5 py-2 text-sm font-mono text-slate-100 outline-none">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1 font-mono">SMS MESSAGE TEXT</label>
          <textarea id="messageInput" rows="3"
            class="w-full bg-slate-950/80 border border-slate-800 focus:border-sky-500 rounded-xl p-3 text-xs font-mono text-slate-100 leading-relaxed outline-none resize-none">Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.</textarea>
        </div>

        <!-- Collapsible Advanced Settings (Keeps Simple Mode Clean!) -->
        <div class="pt-2 border-t border-slate-800/80">
          <button type="button" onclick="toggleAdvanced()" class="w-full flex items-center justify-between text-xs text-slate-400 hover:text-sky-400 py-1 font-mono transition-colors">
            <span class="flex items-center gap-1.5">
              <span>⚙️</span> Advanced Telecom Settings
            </span>
            <span id="advToggleIcon" class="text-slate-500">▼ Expand</span>
          </button>
          
          <div id="advancedDrawer" class="hidden mt-3 space-y-3 p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs">
            <div>
              <label class="block text-[11px] font-mono text-slate-500 mb-1">INGRESS ROUTE CHANNEL</label>
              <select id="routeSelect" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-1.5 text-xs font-mono text-slate-200">
                <option value="domestic_onnet">Domestic On-Net (Ethio/Safaricom)</option>
                <option value="international_ipx">International IPX (Roaming)</option>
                <option value="grey_route">Unlicensed Grey Route / SIM-Box</option>
              </select>
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div>
                <label class="block text-[11px] font-mono text-slate-500 mb-1">CALLING GT</label>
                <input type="text" id="gtInput" value="+251911000000" class="w-full bg-slate-900 border border-slate-800 rounded-lg p-1.5 text-xs font-mono text-slate-200">
              </div>
              <div>
                <label class="block text-[11px] font-mono text-slate-500 mb-1">SIM AGE: <span id="simAgeVal" class="text-sky-400">720h</span></label>
                <input type="range" id="simAgeSlider" min="1" max="1000" value="720" oninput="document.getElementById('simAgeVal').innerText=this.value+'h'" class="w-full h-1 bg-slate-800 rounded">
              </div>
            </div>
          </div>
        </div>

        <button onclick="runInspection()" id="inspectBtn"
          class="w-full rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2.5 px-4 text-xs tracking-wide transition-all shadow-lg shadow-sky-600/20 active:scale-[0.99] flex items-center justify-center gap-2">
          <span>⚡ Run Live Inspection</span>
        </button>

      </div>

      <!-- Results Side-by-Side (7 Cols) -->
      <div class="lg:col-span-7 space-y-4">
        
        <!-- Side-by-Side Comparison -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          
          <!-- Box 1: PAiCore Baseline -->
          <div class="glass-card rounded-2xl p-4 border border-slate-800/80">
            <div class="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">1. PAiCore Baseline (NLP)</div>
            <div class="flex items-center justify-between mb-2">
              <span id="otsVerdictBadge" class="text-xs font-bold font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-400">
                WAITING
              </span>
              <span id="otsConfidence" class="text-xs font-mono text-slate-400 font-semibold">--</span>
            </div>
            <p class="text-[11px] text-slate-400 leading-normal" id="otsExplainer">
              mBERT checks only message text semantics.
            </p>
          </div>

          <!-- Box 2: TelcoShield Result -->
          <div class="glass-card rounded-2xl p-4 border-2 transition-all" id="telcoVerdictCard">
            <div class="text-[11px] font-mono uppercase tracking-wider text-slate-400 mb-2">2. TelcoShield Telecom Edge</div>
            <div class="flex items-center justify-between mb-2">
              <span id="telcoVerdictBadge" class="text-xs font-bold font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-400">
                WAITING
              </span>
              <span id="latencyDisplay" class="text-xs font-mono text-sky-400">-- ms</span>
            </div>
            <p class="text-[11px] text-slate-300 leading-normal font-medium" id="telcoActionDisplay">
              Evaluates text + Sender ID + network route.
            </p>
          </div>

        </div>

        <!-- The "Why it Happened" Callout (Clean & Concise!) -->
        <div id="overrideCallout" style="display:none;" class="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs space-y-1">
          <div class="font-bold flex items-center gap-1.5 text-amber-300">
            <span>⚠️</span> Blind Spot Caught!
          </div>
          <p class="text-[11px] text-amber-200/90 leading-relaxed" id="overrideReasonText">
            The message claims to be a Telebirr payment, but came from a personal SIM card (+2519...). Raw NLP called it legitimate, but TelcoShield blocked it at the network edge.
          </p>
        </div>

        <div id="ruleCallout" style="display:none;" class="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs space-y-1">
          <div class="text-[11px] font-mono text-slate-500 uppercase">Triggered Firewall Rule:</div>
          <div id="ruleText" class="text-xs font-mono text-slate-300"></div>
        </div>

        <!-- Bottom Toggle for CAMARA SIM Swap -->
        <div class="pt-2">
          <button type="button" onclick="toggleCamara()" class="w-full text-left p-3 rounded-xl glass-card border border-cyan-500/20 hover:border-cyan-500/40 transition-colors flex items-center justify-between text-xs text-cyan-400 font-semibold">
            <span class="flex items-center gap-2">
              <span>🌐</span> CAMARA SIM-Swap API Simulator (Zero-Trust Bank Check)
            </span>
            <span id="camaraToggleIcon" class="text-cyan-500">▼ Expand</span>
          </button>
          
          <div id="camaraDrawer" class="hidden mt-3 p-4 rounded-xl bg-slate-950 border border-cyan-500/20 space-y-3 text-xs">
            <div class="flex gap-2">
              <input type="text" id="camaraPhone" value="+251933445566" class="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 font-mono text-xs text-white">
              <button onclick="runCamaraCheck()" class="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold px-3 py-1.5 rounded-lg text-xs">Check SIM Age</button>
            </div>
            <pre id="camaraOutput" class="text-[11px] font-mono text-cyan-300 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">// Click 'Check SIM Age' to test CAMARA API</pre>
          </div>
        </div>

      </div>

    </div>

  </div>

  <footer class="max-w-5xl mx-auto w-full pt-4 mt-6 border-t border-slate-900 text-center text-xs text-slate-600 font-mono">
    TelcoShield Minimal Demo · Powered by PAiCore OpenTextShield v2.11
  </footer>

  <script>
    const SCENARIOS = {
      case4a: {
        sender: "+251933445566",
        text: "Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.",
        route: "domestic_onnet",
        gt: "+251911000000",
        sim_age: 720
      },
      case4b: {
        sender: "telebirr",
        text: "Your telebirr account has been credited with 45,000.00 ETB by ABEBE KEBEDE. Txn ID: 9A8B7C6D. Current Balance: 48,200.00 ETB.",
        route: "domestic_onnet",
        gt: "+251911000000",
        sim_age: 720
      },
      case3: {
        sender: "+251922334455",
        text: "Telebirr Alert: Your account must be linked to Fayda Digital ID within 24 hours to prevent account freeze. Call 0911XXXXXX or share your OTP code with support.",
        route: "domestic_onnet",
        gt: "+251911000000",
        sim_age: 720
      }
    };

    function pickScenario(key, btnElem) {
      document.querySelectorAll('.scenario-pill').forEach(b => b.classList.remove('scenario-active'));
      if (btnElem) btnElem.classList.add('scenario-active');

      const s = SCENARIOS[key];
      document.getElementById('senderInput').value = s.sender;
      document.getElementById('messageInput').value = s.text;
      document.getElementById('routeSelect').value = s.route;
      document.getElementById('gtInput').value = s.gt;
      document.getElementById('simAgeSlider').value = s.sim_age;
      document.getElementById('simAgeVal').innerText = s.sim_age + 'h';
      runInspection();
    }

    function toggleAdvanced() {
      const drawer = document.getElementById('advancedDrawer');
      const icon = document.getElementById('advToggleIcon');
      if (drawer.classList.contains('hidden')) {
        drawer.classList.remove('hidden');
        icon.innerText = "▲ Collapse";
      } else {
        drawer.classList.add('hidden');
        icon.innerText = "▼ Expand";
      }
    }

    function toggleCamara() {
      const drawer = document.getElementById('camaraDrawer');
      const icon = document.getElementById('camaraToggleIcon');
      if (drawer.classList.contains('hidden')) {
        drawer.classList.remove('hidden');
        icon.innerText = "▲ Collapse";
      } else {
        drawer.classList.add('hidden');
        icon.innerText = "▼ Expand";
      }
    }

    async function runInspection() {
      const sender = document.getElementById('senderInput').value;
      const text = document.getElementById('messageInput').value;
      const route = document.getElementById('routeSelect').value;
      const gt = document.getElementById('gtInput').value;
      const simAge = parseFloat(document.getElementById('simAgeSlider').value) || 720.0;
      const btn = document.getElementById('inspectBtn');

      btn.disabled = true;
      btn.innerText = "Inspecting...";

      try {
        const resp = await fetch('/api/inspect', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            sender_id: sender,
            text: text,
            ingress_route: route,
            calling_gt: gt,
            sim_age_hours: simAge
          })
        });
        const data = await resp.json();
        renderCleanResults(data);
      } catch (e) {
        alert("Error: " + e);
      } finally {
        btn.disabled = false;
        btn.innerText = "⚡ Run Live Inspection";
      }
    }

    function renderCleanResults(data) {
      document.getElementById('latencyDisplay').innerText = data.total_latency_ms + " ms";

      // 1. Baseline Card
      const otsBadge = document.getElementById('otsVerdictBadge');
      otsBadge.innerText = data.paicore_nlp_label.toUpperCase();
      document.getElementById('otsConfidence').innerText = (data.paicore_nlp_confidence * 100).toFixed(1) + "%";

      if (data.paicore_nlp_label === 'ham') {
        otsBadge.className = "text-xs font-bold font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
        document.getElementById('otsExplainer').innerText = "mBERT classified text as legitimate (HAM).";
      } else {
        otsBadge.className = "text-xs font-bold font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30";
        document.getElementById('otsExplainer').innerText = "mBERT detected phishing/scam words.";
      }

      // 2. TelcoShield Card
      const telcoCard = document.getElementById('telcoVerdictCard');
      const telcoBadge = document.getElementById('telcoVerdictBadge');
      telcoBadge.innerText = data.final_verdict;

      if (data.final_verdict === 'BLOCKED_FRAUD') {
        telcoBadge.className = "text-xs font-bold font-mono px-2.5 py-1 rounded bg-rose-500/20 text-rose-400 border border-rose-500/40";
        telcoCard.className = "glass-card rounded-2xl p-4 border-2 border-rose-500/50 bg-rose-950/10";
        document.getElementById('telcoActionDisplay').innerText = "Action: DROPPED at SMSC Gateway.";
      } else {
        telcoBadge.className = "text-xs font-bold font-mono px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
        telcoCard.className = "glass-card rounded-2xl p-4 border-2 border-emerald-500/50 bg-emerald-950/10";
        document.getElementById('telcoActionDisplay').innerText = "Action: DELIVERED to subscriber phone.";
      }

      // Override Alert
      const callout = document.getElementById('overrideCallout');
      if (data.metadata_override) {
        callout.style.display = "block";
      } else {
        callout.style.display = "none";
      }

      // Rules
      const ruleBox = document.getElementById('ruleCallout');
      if (data.rule_triggers && data.rule_triggers.length > 0) {
        ruleBox.style.display = "block";
        document.getElementById('ruleText').innerText = data.rule_triggers[0];
      } else {
        ruleBox.style.display = "none";
      }
    }

    async function runCamaraCheck() {
      const phone = document.getElementById('camaraPhone').value;
      const out = document.getElementById('camaraOutput');
      out.innerText = "Querying...";
      try {
        const resp = await fetch('/api/sim-swap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phoneNumber: phone, maxAge: 48 })
        });
        const data = await resp.json();
        out.innerText = JSON.stringify(data, null, 2);
      } catch (e) {
        out.innerText = "Error: " + e;
      }
    }

    window.addEventListener('load', () => {
      runInspection();
    });
  </script>
</body>
</html>
"""


class TelcoShieldHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CLEAN_UI.encode("utf-8"))
        elif self.path == "/health" or self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "mode": "clean_demo"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8")

        try:
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            payload = {}

        if self.path == "/api/inspect":
            sender_id = payload.get("sender_id", "")
            text = payload.get("text", "")
            ingress_route = payload.get("ingress_route", "domestic_onnet")
            calling_gt = payload.get("calling_gt", "+251911000000")
            sim_age_hours = float(payload.get("sim_age_hours", 720.0))

            result = adapter.inspect_message(
                sender_id=sender_id,
                text=text,
                ingress_route=ingress_route,
                calling_gt=calling_gt,
                sim_age_hours=sim_age_hours
            )

            response_data = {
                "sender_id": result.sender_id,
                "message_text": result.message_text,
                "ingress_route": result.ingress_route,
                "calling_gt": result.calling_gt,
                "sim_age_hours": result.sim_age_hours,
                "paicore_nlp_label": result.paicore_nlp_label,
                "paicore_nlp_confidence": result.paicore_nlp_confidence,
                "paicore_processing_time": result.paicore_processing_time,
                "final_verdict": result.final_verdict,
                "threat_severity": result.threat_severity,
                "rule_triggers": result.rule_triggers,
                "metadata_override": result.metadata_override,
                "total_latency_ms": result.total_latency_ms
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))

        elif self.path == "/api/sim-swap":
            phone = payload.get("phoneNumber", "")
            max_age = payload.get("maxAge", 48)

            last_swap = MOCK_SIM_DATABASE.get(phone)
            if last_swap:
                age_hours = (datetime.now(timezone.utc) - last_swap).total_seconds() / 3600
                swapped = age_hours <= max_age
                resp = {
                    "swapped": swapped,
                    "latestSimChange": last_swap.isoformat(),
                    "ageHours": round(age_hours, 1),
                    "action": "BLOCK_TRANSACTION_STEP_UP_BIOMETRICS" if swapped else "ALLOW_TRANSACTION"
                }
            else:
                resp = {
                    "swapped": False,
                    "latestSimChange": "UNKNOWN_CLEAN",
                    "ageHours": 999.0,
                    "action": "ALLOW_TRANSACTION"
                }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def main():
    port = 8090
    server = HTTPServer(("0.0.0.0", port), TelcoShieldHandler)
    print(f"[*] TelcoShield Clean Demo running at http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")


if __name__ == "__main__":
    main()
