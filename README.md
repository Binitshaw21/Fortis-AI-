# 🛡️ Fortis AI: The Autonomous Governance & Security Copilot

**The Winning Project for the Casper Network**  
Instead of building an AI trading agent that takes random market bets, **Fortis AI** is the foundational security and governance infrastructure layer that every DeFi trading agent on Casper must pay to use before executing a transaction.

When an autonomous agent routes yield or interacts with a smart contract, it flies blind to infrastructure risks, flash crashes, and malicious honeypot traps. Fortis AI solves this by acting as a machine-payable API storefront that evaluates market risk and cybersecurity threats in real-time, returning a cryptographic "Go/No-Go" compliance token and logging an immutable audit record on the Casper Testnet via the Odra Framework.

---

## 🏗️ Architecture & Execution Layers

### 1. The Backend Storefront (The x402 Provider)
- **Tech Stack**: Full-stack web application built with **Django**.
- **Casper x402 Protocol**: Built-in middleware (`CasperX402Middleware`) intercepts incoming AI agent queries to `/api/v1/scan/`.
- If an agent sends a query without cryptographic proof of payment (`X-Casper-402-Proof`), the server responds with **HTTP 402 Payment Required** along with a structured JSON invoice (fee: 2.50 CSPR, treasury wallet address, timestamp). Once paid, the scan proceeds automatically.

### 2. The Quantitative Risk Engine (Market Volatility)
- **Tech Stack**: High-performance Python environment powered by **NumPy** and **Pandas**.
- **5,000+ Row Tick Ingestion**: Ingests and processes high-resolution historical tick datasets (5,000+ rows) across multiple assets (`CSPR/USD`, `ETH/USD`, `BTC/USD`, and synthetic flash-crash scenarios).
- **Advanced Analytics**: Computes 20-period rolling Simple Moving Averages (SMA), upper and lower Bollinger Bands ($\pm 2\sigma$ and $\pm 3\sigma$), instantaneous price velocity Z-scores, and order book liquidity depth.
- **Flash Crash Protection**: If an asset experiences an anomalous drawdown or order book liquidity evaporation, Fortis AI immediately flags a `CRITICAL_FLASH_CRASH` and sets a `NO-GO` decision.

### 3. The Infrastructure Security Scanner (Cybersecurity)
- **Network Port Scanning**: Probes target node infrastructure and RPC endpoints for exposed administrative services (SSH 22, MySQL 3306, Redis 6379, EVM Debug 8545).
- **RPC Hijack & Health Sniffer**: Validates network response latency, verifies expected chain ID metadata against known Casper specifications, and checks for MITM SSL/TLS certificate anomalies.
- **Smart Contract Heuristics**: Analyzes destination bytecode and addresses against known vulnerability databases (reentrancy vectors, unverified proxy upgradeability without timelocks, and malicious drainer honeypots).

### 4. The On-Chain Governance Log (Odra Framework)
- **Cryptographic Go/No-Go Token**: If both quantitative and security checks pass, Fortis AI signs a JWT/HMAC compliance token (`tok_casper_...`) with a 120-second TTL.
- **Odra Rust Smart Contract**: Includes a complete Odra Framework smart contract (`fortis_governance_log`) in Rust (`odra_contract/src/lib.rs`) designed for deployment on the Casper Network.
- **Immutable Audit Trail**: The backend bridge generates an SHA-256 hash of the verification payload and records it on-chain, enabling third-party auditors and DeFi protocols to verify agent compliance without trusting off-chain servers.

---

## 🎨 Visually Stunning Dashboard & Playground

As required by modern web design best practices, Fortis AI features an ultra-premium dark-mode UI:
- **Glassmorphic Aesthetics**: Semi-transparent card layouts with backdrop blur (`backdrop-filter: blur(16px)`), neon cyan (`#00f2fe`) and electric purple (`#4facfe`) glowing borders, and smooth hover micro-animations.
- **Live Governance Dashboard**: Real-time metric counters (CSPR Revenue, Scans Processed, Approved vs. Blocked trades), live Chart.js price/volatility streaming, and an Odra on-chain feed.
- **Interactive AI Agent Playground**: A specialized web console (`/playground/`) where users and developers can select AI Agent profiles, trigger synthetic flash crashes or honeypot attacks, and watch the 4-stage visual terminal enforce HTTP 402 micro-payments and log to Odra in real time!

---

## 🚀 Quick Start Guide (Windows)

### Option 1: One-Click Automated PowerShell Setup
Simply open a PowerShell terminal in this directory and run:
```powershell
.\scripts\setup_env.ps1
```
This script will automatically:
1. Create and activate a Python virtual environment (`.venv`).
2. Install all required packages (`Django`, `numpy`, `pandas`, `PyJWT`, `requests`).
3. Run database migrations and generate the 5,000+ row tick dataset.
4. Launch the local Fortis AI Storefront server at `http://127.0.0.1:8000/`.

---

### Option 2: Manual Step-by-Step Setup

1. **Install Dependencies**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Initialize Database & Seeding Data**:
   ```bash
   python backend/manage.py migrate
   python scripts/generate_tick_data.py
   ```

3. **Start the Web Storefront**:
   ```bash
   python backend/manage.py runserver
   ```
   Now open your browser to [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

## 🤖 Simulating an Autonomous AI Agent

To test how an external DeFi AI agent interacts with Fortis AI via the command line, run our included autonomous simulation script:
```bash
python scripts/simulate_agent.py
```
**What you will see in the terminal**:
1. The agent attempts to query `/api/v1/scan/`.
2. Fortis AI intercepts the request and returns **HTTP 402 Payment Required** with invoice `inv_...` for `2.50 CSPR`.
3. The agent simulates paying the fee and re-submits with the `X-Casper-402-Proof` header.
4. The server runs the NumPy 5000-tick volatility analysis, probes ports, logs the SHA-256 hash to Odra on Casper, and returns the signed `GO` compliance token!

---

## 📂 Repository Structure

```
c:/Users/BINIT SHAW/Fortis AI/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── fortis_project/           # Django settings & routing
│   ├── storefront/               # x402 Storefront, Middleware & UI Dashboard
│   ├── risk_engine/              # NumPy/Pandas Volatility Engine & 5000-tick loader
│   ├── security_scanner/         # Network Port Scanner & Smart Contract Auditor
│   └── governance/               # Compliance Token Issuer & Odra Testnet Bridge
├── odra_contract/                # Odra Framework Rust Smart Contract
│   ├── Odra.toml
│   ├── Cargo.toml
│   └── src/lib.rs                # Immutable governance audit log contract for Casper
├── scripts/
│   ├── setup_env.ps1             # PowerShell automation script
│   ├── generate_tick_data.py     # Data generator script
│   └── simulate_agent.py         # Autonomous AI agent client script
└── README.md                     # Documentation
```
