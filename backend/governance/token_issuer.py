"""
Compliance Token Issuer for Fortis AI.
Generates cryptographically signed Go/No-Go tokens that DeFi agents present
to destination smart contracts to verify that infrastructure and market risk checks passed.
"""
import time
import uuid
import jwt
from django.conf import settings


class ComplianceTokenIssuer:
    """
    Issues and verifies cryptographic compliance tokens for Casper DeFi agents.
    """
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or getattr(settings, 'SECRET_KEY', 'fortis-secret-key-default-2026')
        self.issuer_address = getattr(settings, 'FORTIS_TREASURY_ADDRESS', '0x01a2b3c4...fortis_treasury')

    def issue_token(self, agent_id, target_contract, risk_result, security_result):
        """
        Synthesizes risk and security results into a signed JWT compliance token.
        """
        token_id = f"tok_casper_{uuid.uuid4().hex[:12]}"
        now = int(time.time())
        expires_at = now + 120  # Token valid for 120 seconds

        # Determine final decision: GO only if BOTH checks passed/approved
        risk_decision = risk_result.get("decision", "NO-GO")
        sec_decision = security_result.get("decision", "NO-GO")
        
        final_decision = "GO" if (risk_decision == "GO" and sec_decision == "GO") else "NO-GO"
        
        payload = {
            "token_id": token_id,
            "agent_id": agent_id,
            "target_contract": target_contract,
            "decision": final_decision,
            "risk_score": risk_result.get("risk_score", 100.0),
            "market_status": risk_result.get("status", "UNKNOWN"),
            "security_status": security_result.get("status", "UNKNOWN"),
            "issued_at": now,
            "expires_at": expires_at,
            "validator_node": self.issuer_address
        }

        # Cryptographically sign the payload
        signed_jwt = jwt.encode(payload, self.secret_key, algorithm="HS256")

        return {
            "token_id": token_id,
            "decision": final_decision,
            "signed_token": signed_jwt,
            "payload": payload,
            "expires_in_seconds": 120
        }

    def verify_token(self, signed_token_string):
        """
        Decodes and validates an agent's signed token.
        Returns payload if valid, raises ValueError or returns error dict if expired/invalid.
        """
        try:
            payload = jwt.decode(signed_token_string, self.secret_key, algorithms=["HS256"])
            if payload.get("expires_at", 0) < time.time():
                return {"valid": False, "error": "Token expired"}
            return {"valid": True, "payload": payload}
        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token expired"}
        except jwt.InvalidTokenError as e:
            return {"valid": False, "error": f"Invalid token signature: {str(e)}"}
