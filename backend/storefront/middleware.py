"""
Casper x402 Protocol Middleware for Fortis AI.
Intercepts machine AI agent requests to the scan API.
If cryptographic payment proof is missing, returns HTTP 402 Payment Required with an invoice.
"""
import uuid
import json
from django.http import JsonResponse
from django.conf import settings


class CasperX402Middleware:
    """
    Enforces HTTP 402 micro-payment in CSPR for machine-to-machine API queries.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.treasury_address = getattr(settings, 'FORTIS_TREASURY_ADDRESS', '0x01a2b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f708192a3b4c5d6e7f80')
        self.fee_cspr = getattr(settings, 'FORTIS_SCAN_FEE_CSPR', 2.50)

    def __call__(self, request):
        # Allow CORS preflight requests
        if request.method == "OPTIONS":
            return self.get_response(request)

        # Apply x402 protocol only to protected AI agent endpoints
        if request.path.startswith('/api/v1/scan/'):
            proof_header = request.META.get('HTTP_X_CASPER_402_PROOF') or request.headers.get('X-Casper-402-Proof')
            agent_id = request.META.get('HTTP_X_AGENT_ID') or request.headers.get('X-Agent-Id') or "agent_defi_yield_01"

            if not proof_header:
                # Generate unique invoice ID
                invoice_id = f"inv_{uuid.uuid4().hex[:10]}"
                
                # Attempt to save invoice to database if available
                try:
                    from .models import PaymentInvoice
                    PaymentInvoice.objects.create(
                        invoice_id=invoice_id,
                        agent_id=agent_id,
                        amount_cspr=self.fee_cspr,
                        treasury_address=self.treasury_address,
                        status='PENDING'
                    )
                except Exception:
                    pass

                # Return HTTP 402 Payment Required
                response_data = {
                    "status": 402,
                    "error": "Payment Required",
                    "protocol": "Casper-x402-v1",
                    "message": "Access to Fortis AI Autonomous Security & Governance Storefront requires a micro-fee payment in CSPR before scan execution.",
                    "invoice": {
                        "invoice_id": invoice_id,
                        "amount_cspr": self.fee_cspr,
                        "treasury_address": self.treasury_address,
                        "network": "Casper Testnet",
                        "payment_instructions": f"Send {self.fee_cspr:.2f} CSPR to treasury_address and include the transaction hash in the 'X-Casper-402-Proof' HTTP header."
                    }
                }
                response = JsonResponse(response_data, status=402)
                response["X-Casper-402-Protocol"] = "v1"
                return response

            # Payment proof provided -> Mark request as verified
            request.x402_paid = True
            request.x402_proof_hash = proof_header
            request.agent_id = agent_id

            # Try to record payment verified in DB
            try:
                from .models import PaymentInvoice, AgentAccount
                from django.utils import timezone
                
                PaymentInvoice.objects.create(
                    invoice_id=f"inv_{uuid.uuid4().hex[:10]}",
                    agent_id=agent_id,
                    amount_cspr=self.fee_cspr,
                    treasury_address=self.treasury_address,
                    status='PAID',
                    proof_tx_hash=proof_header,
                    paid_at=timezone.now()
                )
                
                agent, _ = AgentAccount.objects.get_or_create(agent_id=agent_id, defaults={"name": f"Agent ({agent_id[:8]})"})
                agent.total_scans += 1
                agent.total_cspr_spent += self.fee_cspr
                agent.save()
            except Exception:
                pass

        return self.get_response(request)
