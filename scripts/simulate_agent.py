#!/usr/bin/env python
"""
Autonomous AI Agent Simulation Client for Fortis AI.
Demonstrates machine-to-machine interaction with the Fortis AI Storefront:
1. Queries the security scan API without payment -> Receives HTTP 402 Payment Required invoice.
2. Pays the micro-fee in CSPR (simulated transaction proof).
3. Re-queries with X-Casper-402-Proof header -> Receives Dual-Threat Scan & Odra Compliance Token.
"""
import sys
import json
import time
import requests

API_URL = "http://127.0.0.1:8000/api/v1/scan/"
AGENT_ID = "CasperYieldBot-Alpha"
TARGET_CONTRACT = "hash-8899aabbccdd1122334455667788"
TARGET_RPC = "http://rpc.testnet.casperlabs.io:7777"
TICKER = "CSPR/USD"

def run_agent_workflow():
    print("="*75)
    print("🤖 AUTONOMOUS DEFI AGENT WORKFLOW: CASPER YIELD HARVEST")
    print("="*75)
    print(f"Agent ID        : {AGENT_ID}")
    print(f"Target Contract : {TARGET_CONTRACT}")
    print(f"Target RPC      : {TARGET_RPC}")
    print(f"Asset Ticker    : {TICKER}")
    print("-"*75)

    payload = {
        "agent_id": AGENT_ID,
        "ticker": TICKER,
        "target_contract": TARGET_CONTRACT,
        "target_rpc": TARGET_RPC
    }

    # Step 1: Initial query without payment proof
    print("\n[Step 1] Agent requesting security & governance clearance from Fortis AI...")
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json", "X-Agent-Id": AGENT_ID},
            timeout=5
        )
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Could not connect to Fortis AI Storefront at http://127.0.0.1:8000/.")
        print("Please ensure the Django development server is running: python backend/manage.py runserver")
        sys.exit(1)

    print(f"Response Status: HTTP {response.status_code} {response.reason}")

    if response.status_code == 402:
        invoice_data = response.json()
        print("\n[!] INTERCEPTED BY CASPER x402 PROTOCOL STOREFRONT [!]")
        print("    Status         : HTTP 402 Payment Required")
        print(f"    Protocol       : {invoice_data.get('protocol')}")
        print(f"    Invoice ID     : {invoice_data['invoice']['invoice_id']}")
        print(f"    Amount Due     : {invoice_data['invoice']['amount_cspr']} CSPR")
        print(f"    Treasury Wallet: {invoice_data['invoice']['treasury_address']}")
        print(f"    Instructions   : {invoice_data['invoice']['payment_instructions']}")
    else:
        print(f"Unexpected response: {response.text}")
        return

    # Step 2: Agent executes micro-payment
    print("\n[Step 2] Agent automatically executing micro-payment on Casper Testnet...")
    time.sleep(1.5)
    payment_proof = f"0xcspr_tx_pay_{int(time.time())}_confirmed"
    print(f"         Transfer Confirmed! Payment Proof TX Hash: {payment_proof}")

    # Step 3: Re-query with payment proof header
    print("\n[Step 3] Re-submitting scan request with X-Casper-402-Proof header...")
    time.sleep(1.0)
    
    headers_with_proof = {
        "Content-Type": "application/json",
        "X-Agent-Id": AGENT_ID,
        "X-Casper-402-Proof": payment_proof
    }
    
    auth_response = requests.post(
        API_URL,
        json=payload,
        headers=headers_with_proof,
        timeout=10
    )

    print(f"Response Status: HTTP {auth_response.status_code} {auth_response.reason}")

    if auth_response.status_code == 200:
        result = auth_response.json()
        print("\n" + "="*75)
        print("🛡️  FORTIS AI DUAL-THREAT ANALYSIS & ODRA GOVERNANCE VERDICT")
        print("="*75)
        
        q_risk = result["dual_threat_analysis"]["quantitative_risk_engine"]
        print(f"\n📈 Layer 1: Quantitative Risk Engine ({q_risk.get('total_ticks_analyzed', 5000)}+ Ticks Analyzed)")
        print(f"   - Risk Score        : {q_risk['risk_score']} / 100")
        print(f"   - Volatility Status : {q_risk['status']}")
        print(f"   - Bollinger Bands   : Upper {q_risk['bollinger_upper_2sig']} | Lower {q_risk['bollinger_lower_2sig']}")
        print(f"   - Z-Score Velocity  : {q_risk['z_score_velocity']}")
        print(f"   - Order Book Depth  : ${q_risk['order_book_depth_usd']:,.2f}")

        i_sec = result["dual_threat_analysis"]["infrastructure_security_scanner"]
        print(f"\n🔐 Layer 2: Infrastructure Cybersecurity Scanner")
        print(f"   - Security Status   : {i_sec['status']}")
        print(f"   - Network Port Scan : Probed ports {i_sec['network_scan']['open_ports']} (RPC Latency: {i_sec['network_scan']['rpc_latency_ms']} ms)")
        print(f"   - Smart Contract    : {i_sec['contract_audit']['reason']}")

        odra = result["odra_on_chain_log"]
        print(f"\n⛓️  Layer 3: Odra Framework On-Chain Governance Log")
        print(f"   - Odra Proof Hash   : {odra['proof_hash']}")
        print(f"   - Casper Tx Hash    : {odra['casper_tx_hash']}")
        print(f"   - Block Height      : #{odra['block_height']} ({odra['network']})")
        print(f"   - Validator Sig     : {odra['validator_signature']}")

        print("\n" + "-"*75)
        verdict = result["final_decision"]
        if verdict == "GO":
            print(f"✅ FINAL VERDICT: {verdict} (APPROVED - SAFE TO EXECUTE)")
            print(f"   Compliance Token ID : {result['compliance_token']['token_id']} (Valid for 120s)")
            print("   Agent may now submit transaction to destination smart contract.")
        else:
            print(f"🛑 FINAL VERDICT: {verdict} (BLOCKED - HIGH RISK DETECTED)")
            print("   Execution halted! Agent capital protected.")
        print("="*75)
    else:
        print(f"Error executing scan: {auth_response.text}")


if __name__ == "__main__":
    run_agent_workflow()
