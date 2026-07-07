"""
Unit Tests for Fortis AI Autonomous Security & Governance Copilot.
Tests all four layers:
1. x402 Storefront & HTTP 402 Middleware
2. NumPy/Pandas Quantitative Risk Engine
3. Infrastructure Security Scanner & Contract Auditor
4. Odra Framework On-Chain Governance Log & Cryptographic Tokens
"""
import json
from django.test import TestCase, Client
from django.urls import reverse

from risk_engine.analyzer import QuantitativeRiskEngine
from security_scanner.network_scanner import NetworkSecurityScanner
from security_scanner.contract_auditor import SmartContractAuditor
from governance.token_issuer import ComplianceTokenIssuer
from governance.odra_bridge import OdraGovernanceBridge


class FortisAILayerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.scan_url = "/api/v1/scan/"
        self.verify_url = "/api/v1/verify/"
        self.stats_url = "/api/v1/stats/"

    def test_layer1_x402_protocol_enforcement(self):
        """
        Verify that requests without X-Casper-402-Proof return HTTP 402 Payment Required.
        """
        response = self.client.post(
            self.scan_url,
            data=json.dumps({"ticker": "CSPR/USD"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 402)
        data = response.json()
        self.assertEqual(data["error"], "Payment Required")
        self.assertEqual(data["protocol"], "Casper-x402-v1")
        self.assertIn("invoice_id", data["invoice"])
        self.assertEqual(data["invoice"]["amount_cspr"], 2.50)

    def test_layer2_quantitative_risk_engine(self):
        """
        Verify NumPy/Pandas engine correctly analyzes normal regimes and catches flash crashes.
        """
        # Test Normal Regime
        engine_normal = QuantitativeRiskEngine(ticker="CSPR/USD")
        res_normal = engine_normal.run_comprehensive_analysis()
        self.assertIn(res_normal["status"], ["SAFE", "ELEVATED_VOLATILITY"])
        self.assertEqual(res_normal["decision"], "GO")
        self.assertGreaterEqual(res_normal["total_ticks_analyzed"], 5000)

        # Test Flash Crash Regime
        engine_crash = QuantitativeRiskEngine(ticker="CSPR-CRASH/USD")
        res_crash = engine_crash.run_comprehensive_analysis()
        self.assertEqual(res_crash["status"], "CRITICAL_FLASH_CRASH")
        self.assertEqual(res_crash["decision"], "NO-GO")
        self.assertIn("FLASH_CRASH_ANOMALY", res_crash["flags"])

    def test_layer3_infrastructure_security_scanner(self):
        """
        Verify network port scanner and smart contract heuristic auditor.
        """
        # Safe contract check
        auditor_safe = SmartContractAuditor(target_contract="hash-8899aabb")
        res_safe = auditor_safe.audit_contract_security()
        self.assertEqual(res_safe["decision"], "GO")
        self.assertEqual(res_safe["status"], "PASSED")

        # Malicious honeypot check
        auditor_scam = SmartContractAuditor(target_contract="hash-deadbeefscam0000")
        res_scam = auditor_scam.audit_contract_security()
        self.assertEqual(res_scam["decision"], "NO-GO")
        self.assertEqual(res_scam["status"], "MALICIOUS_HONEYPOT_DETECTED")
        self.assertEqual(res_scam["severity"], "CRITICAL")

    def test_layer4_odra_governance_and_token_issuer(self):
        """
        Verify cryptographic token signing and Odra SHA-256 testnet hash generation.
        """
        issuer = ComplianceTokenIssuer()
        token_res = issuer.issue_token(
            agent_id="test_agent",
            target_contract="hash-1234",
            risk_result={"decision": "GO", "risk_score": 12.0, "status": "SAFE"},
            security_result={"decision": "GO", "status": "PASSED"}
        )
        self.assertEqual(token_res["decision"], "GO")
        self.assertIn("tok_casper_", token_res["token_id"])

        # Verify decoding
        verify_res = issuer.verify_token(token_res["signed_token"])
        self.assertTrue(verify_res["valid"])
        self.assertEqual(verify_res["payload"]["agent_id"], "test_agent")

        # Verify Odra Bridge hash
        bridge = OdraGovernanceBridge()
        log_res = bridge.log_on_chain(
            agent_id="test_agent",
            target_contract="hash-1234",
            decision="GO",
            risk_score=12.0,
            security_status="PASSED"
        )
        self.assertEqual(len(log_res["proof_hash"]), 64)
        self.assertTrue(log_res["casper_tx_hash"].startswith("0xcasper_"))

    def test_full_successful_scan_workflow(self):
        """
        Verify full API scan workflow when X-Casper-402-Proof header is provided.
        """
        response = self.client.post(
            self.scan_url,
            data=json.dumps({
                "agent_id": "test_bot_007",
                "ticker": "CSPR/USD",
                "target_contract": "hash-8899aabb"
            }),
            content_type="application/json",
            HTTP_X_CASPER_402_PROOF="0xcspr_pay_proof_123456789"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["payment_verified"])
        self.assertEqual(data["final_decision"], "GO")
        self.assertIn("odra_on_chain_log", data)
        self.assertIn("compliance_token", data)

    def test_dashboard_and_stats_endpoints(self):
        """
        Verify UI dashboard and stats API return 200 OK.
        """
        res_dash = self.client.get("/")
        self.assertEqual(res_dash.status_code, 200)

        res_play = self.client.get("/playground/")
        self.assertEqual(res_play.status_code, 200)

        res_stats = self.client.get(self.stats_url)
        self.assertEqual(res_stats.status_code, 200)
        stats_data = res_stats.json()
        self.assertIn("metrics", stats_data)
        self.assertIn("live_chart", stats_data)
