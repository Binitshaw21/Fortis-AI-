"""
Database Models for Fortis AI Storefront.
Tracks AI Agents, x402 Payment Invoices, Scan Requests, and Compliance Tokens.
"""
from django.db import models
from django.utils import timezone


class AgentAccount(models.Model):
    agent_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=150, default="DeFi Yield Agent")
    total_scans = models.PositiveIntegerField(default=0)
    total_cspr_spent = models.FloatField(default=0.0)
    trust_score = models.FloatField(default=95.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.agent_id})"


class PaymentInvoice(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid Verified'),
        ('EXPIRED', 'Expired'),
    ]
    invoice_id = models.CharField(max_length=100, unique=True, db_index=True)
    agent_id = models.CharField(max_length=100, default="anonymous_agent")
    amount_cspr = models.FloatField(default=2.50)
    treasury_address = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    proof_tx_hash = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Invoice {self.invoice_id} ({self.status}) - {self.amount_cspr} CSPR"


class ScanRequest(models.Model):
    DECISION_CHOICES = [
        ('GO', 'GO - Safe to Execute'),
        ('NO-GO', 'NO-GO - Blocked Risk'),
    ]
    request_id = models.CharField(max_length=100, unique=True, db_index=True)
    agent_id = models.CharField(max_length=100)
    ticker = models.CharField(max_length=50, default="CSPR/USD")
    target_contract = models.CharField(max_length=150)
    target_rpc = models.CharField(max_length=200)
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    risk_score = models.FloatField(default=0.0)
    market_status = models.CharField(max_length=100, default="SAFE")
    security_status = models.CharField(max_length=100, default="PASSED")
    proof_hash = models.CharField(max_length=100, db_index=True)
    casper_tx_hash = models.CharField(max_length=120, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Scan {self.request_id} [{self.decision}] - Agent {self.agent_id}"


class ComplianceToken(models.Model):
    token_id = models.CharField(max_length=100, unique=True, db_index=True)
    agent_id = models.CharField(max_length=100)
    target_contract = models.CharField(max_length=150)
    decision = models.CharField(max_length=20)
    signed_jwt = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Token {self.token_id} ({self.decision})"
