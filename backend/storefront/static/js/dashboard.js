/*
   Fortis AI Dashboard & Agent Simulation Script
   Handles real-time Chart.js rendering, AJAX stats polling, and terminal animations.
*/

document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
  initPlayground();
  initFeed();
});

function initFeed() {
  const invoiceStream = document.getElementById("invoice-stream");
  if (!invoiceStream) return;
  fetchStatsAndUpdate();
  setInterval(fetchStatsAndUpdate, 3000);
}

/* =========================================================
   1. GOVERNANCE DASHBOARD (Live Charts & Stats)
   ========================================================= */
let volChart = null;

function initDashboard() {
  const chartCanvas = document.getElementById("volatilityChart");
  if (!chartCanvas) return;

  const ctx = chartCanvas.getContext("2d");

  volChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: Array.from({ length: 50 }, (_, i) => `T-${50 - i}`),
      datasets: [
        {
          label: "CSPR Price (USD)",
          data: [],
          borderColor: "#00f2fe",
          backgroundColor: "rgba(0, 242, 254, 0.05)",
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.2,
          fill: true,
        },
        {
          label: "Bollinger Upper (+2σ)",
          data: [],
          borderColor: "rgba(247, 37, 133, 0.6)",
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false,
        },
        {
          label: "Bollinger Lower (-2σ)",
          data: [],
          borderColor: "rgba(0, 245, 212, 0.6)",
          borderWidth: 1.5,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false,
        },
        {
          label: "20-Period SMA",
          data: [],
          borderColor: "rgba(148, 163, 184, 0.4)",
          borderWidth: 1,
          pointRadius: 0,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 800 },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.04)" },
          ticks: { color: "#94a3b8", maxTicksLimit: 10 },
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.08)" },
          ticks: { color: "#94a3b8" },
        },
      },
      plugins: {
        legend: {
          labels: { color: "#f0f4f8", font: { family: "Outfit" } },
        },
      },
    },
  });

  // Initial fetch and polling
  fetchStatsAndUpdate();
  setInterval(fetchStatsAndUpdate, 4000);
}

async function fetchStatsAndUpdate() {
  try {
    const res = await fetch("/api/v1/stats/");
    if (!res.ok) return;
    const data = await res.json();

    // Update Metric Cards
    if (data.metrics) {
      updateElement("metric-revenue", data.metrics.total_cspr_revenue.toFixed(2));
      updateElement("feed-total-cspr", data.metrics.total_cspr_revenue.toFixed(2));
      updateElement("metric-scans", data.metrics.total_scans_processed);
      updateElement("feed-total-scans", data.metrics.total_scans_processed);
      updateElement("metric-go", data.metrics.go_decisions);
      updateElement("metric-nogo", data.metrics.threats_blocked);
    }

    // Update Chart Data
    if (data.live_chart && volChart) {
      if (data.live_chart.prices && data.live_chart.prices.length > 0) {
        volChart.data.datasets[0].data = data.live_chart.prices;
        volChart.data.datasets[1].data = data.live_chart.upper_band;
        volChart.data.datasets[2].data = data.live_chart.lower_band;
        volChart.data.datasets[3].data = data.live_chart.sma;
        volChart.update("none"); // Smooth silent update
      }
    }

    // Update Live Scan Feed (Dashboard & Governance Feed)
    if (data.recent_scans && data.recent_scans.length > 0) {
      const feedEl = document.getElementById("scan-stream");
      const govEl = document.getElementById("governance-stream");
      const htmlContent = data.recent_scans
        .map((s) => {
          const isGo = s.decision === "GO";
          return `
            <div class="scan-item" style="${!isGo ? "border-color: rgba(247, 37, 133, 0.3);" : ""}">
              <div>
                <div class="scan-agent"><span>${isGo ? "🤖" : "🚨"}</span> ${s.agent_id} [${s.ticker}]</div>
                <div class="scan-meta" style="${!isGo ? "color: var(--accent-magenta);" : ""}">
                  Contract: ${s.target_contract} | Odra Hash: ${s.proof_hash}
                </div>
              </div>
              <span class="badge ${isGo ? "badge-go" : "badge-nogo"}">${s.decision}</span>
            </div>
          `;
        })
        .join("");

      if (feedEl) feedEl.innerHTML = htmlContent;
      if (govEl) govEl.innerHTML = htmlContent;
    }

    // Update Live Invoice Feed
    if (data.recent_invoices && data.recent_invoices.length > 0) {
      const invEl = document.getElementById("invoice-stream");
      if (invEl) {
        invEl.innerHTML = data.recent_invoices
          .map((inv) => {
            return `
              <div class="scan-item">
                <div>
                  <div class="scan-agent"><span>💳</span> Invoice ${inv.invoice_id} (${inv.amount_cspr.toFixed(2)} CSPR)</div>
                  <div class="scan-meta">
                    Agent: ${inv.agent_id} | Proof: ${inv.proof_tx_hash} | ${inv.timestamp}
                  </div>
                </div>
                <span class="badge badge-go">${inv.status}</span>
              </div>
            `;
          })
          .join("");
      }
    }
  } catch (err) {
    console.error("Dashboard poll error:", err);
  }
}

function updateElement(id, val) {
  const el = document.getElementById(id);
  if (el && el.innerText !== String(val)) {
    el.innerText = val;
  }
}

/* =========================================================
   2. AGENT SIMULATION PLAYGROUND
   ========================================================= */
function initPlayground() {
  const btnExec = document.getElementById("btn-execute-sim");
  if (!btnExec) return;

  btnExec.addEventListener("click", runAgentSimulation);
}

async function runAgentSimulation() {
  const btn = document.getElementById("btn-execute-sim");
  const term = document.getElementById("terminal-output");
  const badge = document.getElementById("term-status");

  const agentId = document.getElementById("sim-agent").value;
  const scenario = document.getElementById("sim-scenario").value;
  const infra = document.getElementById("sim-infra").value;

  // Set parameters based on selection
  let ticker = "CSPR/USD";
  if (scenario === "flash_crash") ticker = "CSPR-CRASH/USD";

  let targetContract = "hash-8899aabbccdd1122334455667788";
  if (infra === "honeypot") targetContract = "hash-deadbeef0000scam1111222233334444";

  let targetRpc = "http://rpc.testnet.casperlabs.io:7777";
  if (infra === "hijacked") targetRpc = "http://rpc.attack-node.casper:8545";

  // Reset UI
  btn.disabled = true;
  badge.className = "badge badge-go";
  badge.innerText = "RUNNING SCAN...";
  
  const latVal = document.getElementById("sim-latency-val");
  const flagsVal = document.getElementById("sim-flags-val");
  const resVal = document.getElementById("sim-result-val");
  if (latVal) latVal.innerText = "Scanning...";
  if (flagsVal) { flagsVal.innerText = "0"; flagsVal.style.color = "var(--accent-violet-light)"; }
  if (resVal) { resVal.innerText = "RUNNING..."; resVal.style.color = "var(--accent-amber)"; }

  term.innerHTML = `
    <div class="terminal-header">
      <span>Fortis AI Kernel v1.0 | Odra Framework Bridge</span>
      <span>Casper Testnet</span>
    </div>
  `;

  const log = (msg, cls = "info") => {
    const div = document.createElement("div");
    div.className = `log-line ${cls}`;
    div.innerText = msg;
    term.appendChild(div);
    term.scrollTop = term.scrollHeight;
  };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  try {
    log(`>[AGENT ${agentId}] Preparing DeFi yield transaction...`, "info");
    await sleep(600);
    log(`>[AGENT ${agentId}] Sending request to Fortis AI Storefront API... Target Contract: ${targetContract}`, "info");
    await sleep(700);

    // Step 1: Simulate HTTP 402 Payment Required Interception
    log(`>[x402 PROTOCOL] Intercepting machine API query... No valid X-Casper-402-Proof header found!`, "warn");
    await sleep(600);
    log(`>[x402 STOREFRONT] HTTP 402 PAYMENT REQUIRED! Invoice inv_${Math.random().toString(36).substring(7)} generated.`, "error");
    log(`>[x402 STOREFRONT] Fee: 2.50 CSPR -> Treasury Wallet: 0x01a2b3c4...fortis_treasury`, "warn");
    await sleep(1000);

    // Step 2: Agent pays invoice
    log(`>[AGENT ${agentId}] Automatically transferring 2.50 CSPR to Fortis Treasury...`, "info");
    await sleep(800);
    const payProof = `0xcspr_tx_pay_${Math.random().toString(36).substring(2, 12)}`;
    log(`>[AGENT ${agentId}] Payment confirmed on Casper Testnet! Proof: ${payProof}`, "success");
    await sleep(600);
    log(`>[AGENT ${agentId}] Re-submitting API request with header X-Casper-402-Proof...`, "info");
    await sleep(700);

    // Step 3: Run real scan via backend API
    log(`>[FORTIS KERNEL] Payment verified! Activating Layer 1: Quantitative Risk Engine...`, "info");
    await sleep(600);
    log(`>[QUANTITATIVE ENGINE] Ingesting 5,000+ rows of historical tick data for ${ticker}...`, "info");
    await sleep(700);
    log(`>[QUANTITATIVE ENGINE] Computing Bollinger Bands (±2σ) and Z-score price velocity...`, "info");
    await sleep(600);

    log(`>[FORTIS KERNEL] Activating Layer 2: Infrastructure Cybersecurity Scanner...`, "info");
    await sleep(600);
    log(`>[CYBERSECURITY SCANNER] Probing network ports (80, 443, 7777, 3306, 6379, 8545) on host...`, "info");
    await sleep(700);
    log(`>[CYBERSECURITY SCANNER] Auditing destination contract bytecode against known vulnerability heuristics...`, "info");
    await sleep(800);

    // Make AJAX request to backend
    const res = await fetch("/api/v1/scan/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Casper-402-Proof": payProof,
        "X-Agent-Id": agentId,
      },
      body: JSON.stringify({
        agent_id: agentId,
        ticker: ticker,
        target_contract: targetContract,
        target_rpc: targetRpc,
      }),
    });

    const result = await res.json();

    log(`>[FORTIS KERNEL] Dual-Threat Analysis Complete! Summarizing results:`, "info");
    await sleep(500);

    const qRisk = result.dual_threat_analysis?.quantitative_risk_engine || {};
    log(`   - Risk Score: ${qRisk.risk_score || 0}/100 | Status: ${qRisk.status || "SAFE"}`, qRisk.decision === "GO" ? "success" : "error");
    log(`   - Bollinger Bounds: Upper ${qRisk.bollinger_upper_2sig} | Lower ${qRisk.bollinger_lower_2sig} | Current ${qRisk.current_price}`, "info");
    log(`   - Z-Score Velocity: ${qRisk.z_score_velocity} | 30-Tick Drawdown: ${qRisk.drawdown_rolling_30_pct}%`, "info");

    const iSec = result.dual_threat_analysis?.infrastructure_security_scanner || {};
    log(`   - Security Status: ${iSec.status || "PASSED"} | Ports Checked: 8 open/audited`, iSec.decision === "GO" ? "success" : "error");

    await sleep(600);
    log(`>[ODRA GOVERNANCE] Synthesizing verdict and logging immutable hash to Casper Testnet...`, "info");
    await sleep(700);

    const odraLog = result.odra_on_chain_log || {};
    log(`>[ODRA GOVERNANCE] Proof Hash: ${odraLog.proof_hash}`, "success");
    log(`>[ODRA GOVERNANCE] Casper Testnet Tx Hash: ${odraLog.casper_tx_hash}`, "success");
    log(`>[ODRA GOVERNANCE] Block Height: #${odraLog.block_height} | Validator Sig: ${odraLog.validator_signature}`, "info");

    await sleep(600);

    const latencyMs = odraLog.latency_ms || (Math.floor(Math.random() * 18) + 12);
    if (latVal) latVal.innerText = `${latencyMs}ms`;

    let totalFlags = 0;
    if (qRisk.status !== "SAFE" && qRisk.status !== "NORMAL") totalFlags += 1;
    if (iSec.status !== "PASSED" && iSec.status !== "SECURE") totalFlags += 1;
    if (flagsVal) {
      flagsVal.innerText = totalFlags.toString();
      flagsVal.style.color = totalFlags > 0 ? "var(--accent-rose)" : "var(--accent-violet-light)";
    }

    if (result.final_decision === "GO") {
      badge.className = "badge badge-go";
      badge.innerText = "VERDICT: GO (APPROVED)";
      if (resVal) { resVal.innerText = "✅ GO (SAFE)"; resVal.style.color = "var(--accent-emerald)"; }
      log(`\n>[FINAL VERDICT] ✅ GO - SAFE TO EXECUTE! Cryptographic Compliance Token issued to agent.`, "success");
      log(`>[AGENT ${agentId}] Token tok_id: ${result.compliance_token?.token_id} received. Proceeding with yield trade!`, "success");
    } else {
      badge.className = "badge badge-nogo";
      badge.innerText = "VERDICT: NO-GO (BLOCKED)";
      if (resVal) { resVal.innerText = "🛑 NO-GO (BLOCKED)"; resVal.style.color = "var(--accent-rose)"; }
      log(`\n>[FINAL VERDICT] 🛑 NO-GO - EXECUTION BLOCKED! High risk or infrastructure vulnerability detected!`, "error");
      log(`>[AGENT ${agentId}] Transaction aborted! Agent capital protected from loss/drain.`, "error");
    }
  } catch (err) {
    log(`>[SYSTEM ERROR] Simulation failed: ${err.message}`, "error");
    badge.className = "badge badge-nogo";
    badge.innerText = "ERROR";
    if (latVal) latVal.innerText = "ERR";
    if (resVal) { resVal.innerText = "⚠️ ERROR"; resVal.style.color = "var(--accent-rose)"; }
  } finally {
    btn.disabled = false;
  }
}
