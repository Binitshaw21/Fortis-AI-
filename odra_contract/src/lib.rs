//! Fortis AI Governance Log Smart Contract
//! Built with the Odra Framework for the Casper Network.
//!
//! This contract maintains an immutable, cryptographically verifiable audit trail
//! of all dual-threat analysis checks (Quantitative Risk + Infrastructure Security)
//! performed by Fortis AI for DeFi trading agents on Casper.

use odra::prelude::*;
use odra::{Address, Var, Mapping, Event};

/// Structure representing an immutable governance compliance record.
#[odra::odra_type]
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ComplianceRecord {
    pub agent_id: String,
    pub target_contract: String,
    pub decision: String,          // "GO" or "NO-GO"
    pub risk_score_scaled: u32,    // Risk score scaled by 100 (e.g. 1245 = 12.45%)
    pub security_status: String,   // e.g., "PASSED", "BLOCKED_PORT_EXPOSED", "FLASH_CRASH_DETECTED"
    pub timestamp: u64,            // Unix timestamp
    pub validator_signature: String, // Cryptographic signature of Fortis AI node
}

/// Event emitted whenever a new governance compliance check is recorded on-chain.
#[derive(Event, Debug, PartialEq, Eq)]
pub struct ComplianceCheckLogged {
    pub proof_hash: String,
    pub agent_id: String,
    pub target_contract: String,
    pub decision: String,
    pub timestamp: u64,
}

/// The Fortis Governance Log Contract definition.
#[odra::module]
pub struct FortisGovernanceLog {
    /// Admin / Treasury address authorized to write verified scan logs.
    admin: Var<Address>,
    /// Mapping from SHA-256 Proof Hash to the full ComplianceRecord.
    records: Mapping<String, ComplianceRecord>,
    /// Mapping to track total scan count per Agent ID.
    agent_scan_counts: Mapping<String, u32>,
    /// Global statistics
    total_scans_logged: Var<u32>,
    total_go_decisions: Var<u32>,
    total_no_go_decisions: Var<u32>,
}

#[odra::module]
impl FortisGovernanceLog {
    /// Initialize the contract, setting the caller as the Fortis AI admin.
    #[odra::init]
    pub fn init(&mut self) {
        self.admin.set(self.env().caller());
        self.total_scans_logged.set(0);
        self.total_go_decisions.set(0);
        self.total_no_go_decisions.set(0);
    }

    /// Logs an immutable governance check onto the Casper blockchain.
    /// Only the authorized Fortis AI backend validator can invoke this function.
    pub fn log_compliance_check(
        &mut self,
        proof_hash: String,
        agent_id: String,
        target_contract: String,
        decision: String,
        risk_score_scaled: u32,
        security_status: String,
        timestamp: u64,
        validator_signature: String,
    ) {
        // Enforce that only the admin (Fortis AI node) can log official compliance records
        let caller = self.env().caller();
        let admin_addr = self.admin.get_or_default();
        if caller != admin_addr {
            self.env().revert(FortisError::UnauthorizedCaller);
        }

        // Prevent overwriting existing proof hashes to guarantee immutability
        if self.records.get(&proof_hash).is_some() {
            self.env().revert(FortisError::RecordAlreadyExists);
        }

        let record = ComplianceRecord {
            agent_id: agent_id.clone(),
            target_contract: target_contract.clone(),
            decision: decision.clone(),
            risk_score_scaled,
            security_status,
            timestamp,
            validator_signature,
        };

        // Write the immutable record to on-chain storage
        self.records.set(&proof_hash, record);

        // Update global analytics counters
        let current_total = self.total_scans_logged.get_or_default();
        self.total_scans_logged.set(current_total + 1);

        if decision == "GO" {
            let go_count = self.total_go_decisions.get_or_default();
            self.total_go_decisions.set(go_count + 1);
        } else {
            let nogo_count = self.total_no_go_decisions.get_or_default();
            self.total_no_go_decisions.set(nogo_count + 1);
        }

        // Update agent-specific usage statistics
        let agent_count = self.agent_scan_counts.get_or_default(&agent_id);
        self.agent_scan_counts.set(&agent_id, agent_count + 1);

        // Emit on-chain event for Casper indexers and UI monitors
        self.env().emit_event(ComplianceCheckLogged {
            proof_hash,
            agent_id,
            target_contract,
            decision,
            timestamp,
        });
    }

    /// Retrieves an immutable compliance record by its SHA-256 proof hash.
    pub fn get_compliance_record(&self, proof_hash: String) -> Option<ComplianceRecord> {
        self.records.get(&proof_hash)
    }

    /// Verifies if a specific proof hash exists and returned a "GO" decision.
    pub fn is_approved_for_execution(&self, proof_hash: String) -> bool {
        match self.records.get(&proof_hash) {
            Some(record) => record.decision == "GO",
            None => false,
        }
    }

    /// Returns the global scan statistics: (total_scans, total_go, total_no_go).
    pub fn get_global_stats(&self) -> (u32, u32, u32) {
        (
            self.total_scans_logged.get_or_default(),
            self.total_go_decisions.get_or_default(),
            self.total_no_go_decisions.get_or_default(),
        )
    }

    /// Returns the number of scans executed by a specific agent.
    pub fn get_agent_scan_count(&self, agent_id: String) -> u32 {
        self.agent_scan_counts.get_or_default(&agent_id)
    }

    /// Allows the admin to transfer ownership to a new validator node address.
    pub fn transfer_admin(&mut self, new_admin: Address) {
        let caller = self.env().caller();
        if caller != self.admin.get_or_default() {
            self.env().revert(FortisError::UnauthorizedCaller);
        }
        self.admin.set(new_admin);
    }
}

/// Custom error codes for the Fortis Governance contract.
#[odra::odra_error]
pub enum FortisError {
    UnauthorizedCaller = 1,
    RecordAlreadyExists = 2,
    InvalidHashLength = 3,
}

#[cfg(test)]
mod tests {
    use super::*;
    use odra::host::Deployer;

    #[test]
    fn test_governance_logging() {
        let mut contract = FortisGovernanceLog::deploy();
        
        let proof_hash = "a1b2c3d4e5f60718293a4b5c6d7e8f901234567890abcdef1234567890abcdef".to_string();
        let agent_id = "agent_casper_yield_01".to_string();
        let target_contract = "hash-99887766554433221100ffeeddccbbaa".to_string();
        let decision = "GO".to_string();
        let risk_score_scaled = 1450; // 14.50%
        let security_status = "PASSED_ALL_CHECKS".to_string();
        let timestamp = 1783459200;
        let validator_sig = "sig_ed25519_fortis_treasury_valid".to_string();

        contract.log_compliance_check(
            proof_hash.clone(),
            agent_id.clone(),
            target_contract.clone(),
            decision.clone(),
            risk_score_scaled,
            security_status.clone(),
            timestamp,
            validator_sig.clone(),
        );

        let record = contract.get_compliance_record(proof_hash.clone()).unwrap();
        assert_eq!(record.agent_id, agent_id);
        assert_eq!(record.decision, "GO");
        assert!(contract.is_approved_for_execution(proof_hash));

        let (total, go, no_go) = contract.get_global_stats();
        assert_eq!(total, 1);
        assert_eq!(go, 1);
        assert_eq!(no_go, 0);
    }
}
