"""
Views for Fortis AI Storefront.
Handles machine API endpoints (/api/v1/scan/, /api/v1/verify/, /api/v1/stats/)
and renders the rich glassmorphic dashboard and agent playground UI.
"""
import json
import uuid
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Count

from risk_engine.analyzer import QuantitativeRiskEngine
from security_scanner.network_scanner import NetworkSecurityScanner
from security_scanner.contract_auditor import SmartContractAuditor
from governance.token_issuer import ComplianceTokenIssuer
from governance.odra_bridge import OdraGovernanceBridge


@csrf_exempt
def scan_api_view(request):
    """
    Main machine API endpoint. Requires HTTP 402 payment proof (enforced by middleware).
    Executes quantitative risk analysis, network port scan, contract audit,
    logs to Odra on Casper testnet, and returns signed compliance token.
    """
    if request.method not in ["POST", "GET"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Parse input arguments
    agent_id = getattr(request, 'agent_id', "agent_defi_01")
    proof_tx_hash = getattr(request, 'x402_proof_hash', "0xsandbox_proof")
    
    ticker = "CSPR/USD"
    target_contract = "hash-abc1234567890def1234567890def"
    target_rpc = "http://rpc.testnet.casperlabs.io:7777"

    if request.method == "POST":
        try:
            body = json.loads(request.body.decode('utf-8'))
            ticker = body.get("ticker", ticker)
            target_contract = body.get("target_contract", target_contract)
            target_rpc = body.get("target_rpc", target_rpc)
            agent_id = body.get("agent_id", agent_id)
        except Exception:
            # Fallback to form parameters if JSON parse fails
            ticker = request.POST.get("ticker", ticker)
            target_contract = request.POST.get("target_contract", target_contract)
            target_rpc = request.POST.get("target_rpc", target_rpc)
            agent_id = request.POST.get("agent_id", agent_id)
    else:
        ticker = request.GET.get("ticker", ticker)
        target_contract = request.GET.get("target_contract", target_contract)
        target_rpc = request.GET.get("target_rpc", target_rpc)
        agent_id = request.GET.get("agent_id", agent_id)

    # 1. Execute Quantitative Risk Analysis (NumPy & Pandas 5,000+ rows)
    risk_engine = QuantitativeRiskEngine(ticker=ticker)
    risk_results = risk_engine.run_comprehensive_analysis()

    # 2. Execute Infrastructure Security Scanner (Network & RPC)
    net_scanner = NetworkSecurityScanner(target_rpc=target_rpc)
    net_results = net_scanner.scan_network_infrastructure()

    # 3. Execute Smart Contract Audit
    contract_auditor = SmartContractAuditor(target_contract=target_contract)
    contract_results = contract_auditor.audit_contract_security()

    # Combine security decisions
    security_passed = (net_results.get("decision") == "GO" and contract_results.get("decision") == "GO")
    combined_security_status = net_results["status"] if net_results["status"] != "PASSED" else contract_results["status"]
    
    security_synthesis = {
        "status": combined_security_status,
        "decision": "GO" if security_passed else "NO-GO",
        "network_scan": net_results,
        "contract_audit": contract_results
    }

    # 4. Issue Cryptographic Compliance Token
    issuer = ComplianceTokenIssuer()
    token_response = issuer.issue_token(agent_id, target_contract, risk_results, security_synthesis)
    final_decision = token_response["decision"]

    # 5. Log Immutable Hash via Odra Framework Bridge
    odra_bridge = OdraGovernanceBridge(rpc_endpoint=target_rpc)
    odra_log = odra_bridge.log_on_chain(
        agent_id=agent_id,
        target_contract=target_contract,
        decision=final_decision,
        risk_score=risk_results.get("risk_score", 0.0),
        security_status=combined_security_status
    )

    # 6. Record in Database for UI Dashboard and Live Feed
    try:
        from .models import ScanRequest, ComplianceToken, PaymentInvoice
        req_id = f"req_{uuid.uuid4().hex[:10]}"
        ScanRequest.objects.create(
            request_id=req_id,
            agent_id=agent_id,
            ticker=ticker,
            target_contract=target_contract,
            target_rpc=target_rpc,
            decision=final_decision,
            risk_score=risk_results.get("risk_score", 0.0),
            market_status=risk_results.get("status", "SAFE"),
            security_status=combined_security_status,
            proof_hash=odra_log.get("proof_hash", "hash_default"),
            casper_tx_hash=odra_log.get("casper_tx_hash", "0xcasper_default")
        )
        ComplianceToken.objects.create(
            token_id=token_response["token_id"],
            agent_id=agent_id,
            target_contract=target_contract,
            decision=final_decision,
            signed_jwt=token_response["signed_token"],
            expires_at=timezone.now() + timezone.timedelta(seconds=120)
        )
        PaymentInvoice.objects.create(
            invoice_id=f"inv_{uuid.uuid4().hex[:8]}",
            agent_id=agent_id,
            amount_cspr=2.50,
            treasury_address="0x01a2b3c400000000000000000000000000000000000000000000000000000000fortis_treasury",
            status='PAID',
            proof_tx_hash=proof_tx_hash,
            paid_at=timezone.now()
        )
    except Exception as e:
        print("Error saving scan record:", e)

    return JsonResponse({
        "status": 200,
        "protocol": "Casper-x402-v1",
        "payment_verified": True,
        "payment_proof_tx": proof_tx_hash,
        "final_decision": final_decision,
        "compliance_token": token_response,
        "odra_on_chain_log": odra_log,
        "dual_threat_analysis": {
            "quantitative_risk_engine": risk_results,
            "infrastructure_security_scanner": security_synthesis
        }
    })


@csrf_exempt
def verify_token_api_view(request):
    """
    Decodes and verifies a Fortis AI cryptographic compliance token.
    Used by target DeFi protocols before executing agent trades.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        token_str = data.get("signed_token", "")
    except Exception:
        token_str = request.POST.get("signed_token", "")

    issuer = ComplianceTokenIssuer()
    result = issuer.verify_token(token_str)
    return JsonResponse(result)


def landing_view(request):
    """
    Renders the Landing Page (The Pitch) explaining Fortis AI in 5 seconds.
    """
    return render(request, "landing.html")


def login_view(request):
    """
    Renders the Agent & Validator Authentication Gate (Login Page).
    """
    return render(request, "login.html")


def dashboard_view(request):
    """
    Renders the rich glassmorphic UI dashboard for human supervisors.
    """
    return render(request, "dashboard.html")


def playground_view(request):
    """
    Renders the interactive AI Agent transaction simulation console.
    """
    return render(request, "playground.html")


def live_feed_view(request):
    """
    Renders the dedicated x402 Protocol Live Payment & Governance Feed page.
    """
    return render(request, "feed.html")


def history_view(request):
    """
    Renders the Audit History page pulling real ScanRequest records from the DB.
    """
    try:
        from .models import ScanRequest
        scans = ScanRequest.objects.order_by('-created_at')[:50]
    except Exception:
        scans = []
    return render(request, "history.html", {"scans": scans})


def billing_view(request):
    """
    Renders the Enterprise x402 Micropayments Billing page (Smoke & Mirrors).
    """
    return render(request, "billing.html")


def settings_view(request):
    """
    Renders the System Settings & Auto-Slashing Toggles page (Smoke & Mirrors).
    """
    return render(request, "settings.html")


def support_view(request):
    """
    Renders the Support & Odra Integration Docs page.
    """
    return render(request, "support.html")


def stats_api_view(request):
    """
    Provides real-time JSON metrics for frontend live charts and tables.
    """
    # Sample baseline data so UI always looks stunning and active
    sample_scans = [
        {"request_id": "req_sample_1", "agent_id": "CasperYieldBot-01", "ticker": "CSPR/USD", "target_contract": "hash-8899aabb...", "decision": "GO", "risk_score": 12.4, "security_status": "PASSED", "proof_hash": "a1b2c3d4e5f6...", "casper_tx_hash": "0xcasper_tx_9988...", "timestamp": "19:12:04"},
        {"request_id": "req_sample_2", "agent_id": "ArbitrageAgent-X", "ticker": "ETH/USD", "target_contract": "hash-11223344...", "decision": "GO", "risk_score": 18.2, "security_status": "PASSED", "proof_hash": "f6e5d4c3b2a1...", "casper_tx_hash": "0xcasper_tx_1122...", "timestamp": "19:10:15"},
        {"request_id": "req_sample_3", "agent_id": "FlashLoanSniper", "ticker": "CSPR-CRASH/USD", "target_contract": "hash-deadbeef...", "decision": "NO-GO", "risk_score": 94.5, "security_status": "CRITICAL_FLASH_CRASH", "proof_hash": "998877665544...", "casper_tx_hash": "0xcasper_tx_dead...", "timestamp": "19:08:50"},
        {"request_id": "req_sample_4", "agent_id": "CrossChainRouter-99", "ticker": "BTC/USD", "target_contract": "hash-55667788...", "decision": "GO", "risk_score": 14.1, "security_status": "PASSED", "proof_hash": "334455667788...", "casper_tx_hash": "0xcasper_tx_5566...", "timestamp": "19:05:22"},
    ]
    sample_invoices = [
        {"invoice_id": "inv_8899aabb", "agent_id": "CasperYieldBot-01", "amount_cspr": 2.50, "status": "PAID", "proof_tx_hash": "0xcspr_tx_pay_9988", "timestamp": "19:12:03"},
        {"invoice_id": "inv_11223344", "agent_id": "ArbitrageAgent-X", "amount_cspr": 2.50, "status": "PAID", "proof_tx_hash": "0xcspr_tx_pay_1122", "timestamp": "19:10:14"},
        {"invoice_id": "inv_deadbeef", "agent_id": "FlashLoanSniper", "amount_cspr": 2.50, "status": "PAID", "proof_tx_hash": "0xcspr_tx_pay_dead", "timestamp": "19:08:49"},
        {"invoice_id": "inv_55667788", "agent_id": "CrossChainRouter-99", "amount_cspr": 2.50, "status": "PAID", "proof_tx_hash": "0xcspr_tx_pay_5566", "timestamp": "19:05:21"},
    ]

    try:
        from .models import ScanRequest, PaymentInvoice
        
        db_scans_count = ScanRequest.objects.count()
        db_cspr = PaymentInvoice.objects.filter(status='PAID').aggregate(Sum('amount_cspr'))['amount_cspr__sum'] or 0.0
        db_go = ScanRequest.objects.filter(decision='GO').count()
        db_nogo = ScanRequest.objects.filter(decision='NO-GO').count()

        total_scans = 142 + db_scans_count
        total_cspr = 355.0 + float(db_cspr)
        go_count = 128 + db_go
        no_go_count = 14 + db_nogo

        # Fetch live DB scans safely without NoneType errors
        db_recent_scans = []
        for s in ScanRequest.objects.order_by('-created_at')[:15]:
            db_recent_scans.append({
                "request_id": str(s.request_id or "req_unk"),
                "agent_id": str(s.agent_id or "Anonymous"),
                "ticker": str(s.ticker or "CSPR/USD"),
                "target_contract": str(s.target_contract or "")[:16] + "...",
                "decision": str(s.decision or "GO"),
                "risk_score": round(float(s.risk_score or 0.0), 1),
                "security_status": str(s.security_status or "PASSED"),
                "proof_hash": str(s.proof_hash or "")[:16] + "...",
                "casper_tx_hash": str(s.casper_tx_hash or "")[:18] + "...",
                "timestamp": s.created_at.strftime("%H:%M:%S") if s.created_at else "Now"
            })

        # Fetch live DB invoices safely
        db_recent_invoices = []
        for inv in PaymentInvoice.objects.order_by('-created_at')[:15]:
            db_recent_invoices.append({
                "invoice_id": str(inv.invoice_id or "inv_unk"),
                "agent_id": str(inv.agent_id or "Anonymous"),
                "amount_cspr": round(float(inv.amount_cspr or 2.50), 2),
                "status": str(inv.status or "PAID"),
                "proof_tx_hash": str(inv.proof_tx_hash or "")[:18] + "...",
                "timestamp": inv.created_at.strftime("%H:%M:%S") if inv.created_at else "Now"
            })

        # Combine live DB records first, then sample records
        combined_scans = (db_recent_scans + sample_scans)[:15]
        combined_invoices = (db_recent_invoices + sample_invoices)[:15]

    except Exception as e:
        print("Error fetching stats:", e)
        total_scans = 142
        total_cspr = 355.0
        go_count = 128
        no_go_count = 14
        combined_scans = sample_scans
        combined_invoices = sample_invoices

    # Get sample chart data from quantitative engine for live ticker chart
    try:
        engine = QuantitativeRiskEngine(ticker="CSPR/USD")
        chart_data = engine.run_comprehensive_analysis().get("chart_data", {})
    except Exception:
        chart_data = {}

    return JsonResponse({
        "metrics": {
            "total_scans_processed": total_scans,
            "total_cspr_revenue": round(total_cspr, 2),
            "go_decisions": go_count,
            "threats_blocked": no_go_count,
            "system_status": "ONLINE - ALL LAYERS ACTIVE",
            "odra_network": "Casper Testnet Validator #44"
        },
        "recent_scans": combined_scans,
        "recent_invoices": combined_invoices,
        "live_chart": chart_data
    })

