"""
Unit test suite for FLASHWINDOW Reference Prototype Engine
Tests:
1. INV-01: Unauthorized Origin detection
2. INV-02: Content-Hash Mismatch detection
3. INV-03: Security Downgrade detection
4. INV-04: Transient Regression detection
5. INV-05: Multi-Vantage Split-View consensus
6. Ledger integrity: Both pointer breaks AND payload field tampering
7. Merkle tree and cryptographically signed witness receipt verification
8. Bounded UCB1 contextual bandit scheduling and reward updating
9. RFC 8785 JSON Canonicalization Scheme (JCS) compliance
"""

import unittest
import time
import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from benchmark_prototype.flashwindow_engine import (
    FlashWindowEngine,
    PolicyConfiguration,
    ManifestSnapshot,
    MicroProbeTelemetry,
    AlertSeverity,
    InvariantID,
    TemporalStateMachine,
    MultiVantageArbitrator,
    DeterministicInvariantEngine,
    BoundedAITriage,
    HashChainedEvidenceLedger,
    canonicalize_jcs
)

class TestFlashWindowEngine(unittest.TestCase):
    def setUp(self):
        self.policy = PolicyConfiguration(
            approved_origins={"updates.vendor.com", "cdn.vendor.com"},
            version_catalog={"1.0.0": "hash_canonical_v1", "1.1.0": "hash_canonical_v2"},
            require_https=True,
            require_signatures=True,
            consensus_threshold=0.67,
            max_regression_dwell_sec=900.0
        )
        self.invariants = DeterministicInvariantEngine(self.policy)

    def test_inv01_unauthorized_origin(self):
        """INV-01: Flag download URLs pointing outside vendor allowlist"""
        legit_snap = ManifestSnapshot(
            version="1.0.0",
            download_url="https://updates.vendor.com/pkg.tar.gz",
            payload_sha256="hash_canonical_v1",
            signature_present=True,
            signature_valid=True
        )
        violations_legit = self.invariants.verify_manifest(legit_snap, False, 0.0, False, 1.0)
        self.assertEqual(len(violations_legit), 0)

        bad_snap = ManifestSnapshot(
            version="1.0.0",
            download_url="https://malicious-mirror.evil.org/pkg.tar.gz",
            payload_sha256="hash_canonical_v1",
            signature_present=True,
            signature_valid=True
        )
        violations_bad = self.invariants.verify_manifest(bad_snap, False, 0.0, False, 1.0)
        self.assertEqual(len(violations_bad), 1)
        self.assertEqual(violations_bad[0].invariant_id, InvariantID.INV_01_UNAUTHORIZED_ORIGIN)
        self.assertEqual(violations_bad[0].severity, AlertSeverity.CRITICAL)

    def test_inv02_content_hash_mismatch(self):
        """INV-02: Detect binary hash mismatch against canonical version catalog"""
        bad_hash_snap = ManifestSnapshot(
            version="1.0.0",
            download_url="https://updates.vendor.com/pkg.tar.gz",
            payload_sha256="hash_compromised_tampered_bits",
            signature_present=True,
            signature_valid=True
        )
        violations = self.invariants.verify_manifest(bad_hash_snap, False, 0.0, False, 1.0)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].invariant_id, InvariantID.INV_02_CONTENT_HASH_MISMATCH)
        self.assertEqual(violations[0].severity, AlertSeverity.CRITICAL)

    def test_inv03_security_downgrade(self):
        """INV-03: Catch plaintext HTTP transport and missing/invalid signatures"""
        http_snap = ManifestSnapshot(
            version="1.0.0",
            download_url="http://updates.vendor.com/pkg.tar.gz",
            payload_sha256="hash_canonical_v1",
            signature_present=True,
            signature_valid=True,
            protocol="http"
        )
        violations_http = self.invariants.verify_manifest(http_snap, False, 0.0, False, 1.0)
        self.assertIn(InvariantID.INV_03_SECURITY_DOWNGRADE, [v.invariant_id for v in violations_http])

        unsigned_snap = ManifestSnapshot(
            version="1.0.0",
            download_url="https://updates.vendor.com/pkg.tar.gz",
            payload_sha256="hash_canonical_v1",
            signature_present=False,
            signature_valid=False,
            protocol="https"
        )
        violations_unsigned = self.invariants.verify_manifest(unsigned_snap, False, 0.0, False, 1.0)
        self.assertIn(InvariantID.INV_03_SECURITY_DOWNGRADE, [v.invariant_id for v in violations_unsigned])

    def test_inv04_transient_regression(self):
        """INV-04: Ephemeral A -> B -> A state reversion within max dwell time"""
        sm = TemporalStateMachine(max_dwell_sec=300.0)
        t0 = 1000.0
        # A
        is_reg, _, _ = sm.observe("hash_legit_A", t0)
        self.assertFalse(is_reg)
        # B
        is_reg, _, _ = sm.observe("hash_malicious_B", t0 + 60.0)
        self.assertFalse(is_reg)
        # A (Revert within 120s <= 300s)
        is_reg, prev, dwell = sm.observe("hash_legit_A", t0 + 120.0)
        self.assertTrue(is_reg)
        self.assertEqual(prev, "hash_malicious_B")
        self.assertEqual(dwell, 60.0)

    def test_inv05_split_view_consensus(self):
        """INV-05: Multi-vantage consensus detects divergent responses across nodes"""
        arbitrator = MultiVantageArbitrator(consensus_threshold=0.67)
        vantages = {
            "node_us_east": "hash_legit",
            "node_us_west": "hash_legit",
            "node_eu_central": "hash_legit",
            "node_ap_southeast": "hash_tampered_target",
            "node_sa_east": "hash_tampered_target"
        }
        is_split, consensus_hash, ratio, clusters = arbitrator.evaluate_vantages(vantages)
        self.assertTrue(is_split)
        self.assertEqual(consensus_hash, "hash_legit")
        self.assertAlmostEqual(ratio, 0.60)  # 3/5 = 0.60 < 0.67 threshold

    def test_evidence_ledger_chain_break_detection(self):
        """Verify that any post-hoc pointer alteration breaks hash-chain verification"""
        ledger = HashChainedEvidenceLedger()
        for i in range(5):
            ledger.append(
                {"target_endpoint": f"https://updates.vendor.com/v{i}", "vantage_id": "us-east"},
                violations=[],
                priority=0.1
            )
        valid, count = ledger.verify_integrity()
        self.assertTrue(valid)
        self.assertEqual(count, 5)

        # Mutate hash pointer
        ledger.records[2].record_hash = "deadbeef" * 8
        valid_tampered, fail_idx = ledger.verify_integrity()
        self.assertFalse(valid_tampered)
        self.assertEqual(fail_idx, 2)

    def test_evidence_ledger_payload_tamper_detection(self):
        """
        CRITICAL SECURITY TEST (F-05):
        Verify that mutating ANY record payload field (e.g. target_endpoint) WITHOUT modifying
        stored hashes is immediately caught by cryptographic payload recomputation.
        """
        ledger = HashChainedEvidenceLedger()
        for i in range(5):
            ledger.append(
                {"target_endpoint": f"https://updates.vendor.com/pkg_{i}.tar.gz", "vantage_id": "us-east"},
                violations=[],
                priority=0.1
            )
        valid, count = ledger.verify_integrity()
        self.assertTrue(valid)

        # Adversary quietly modifies the target_endpoint payload inside record #2
        ledger.records[2].target_endpoint = "https://unauthorized-attacker-c2.com/trojan.tar.gz"

        # verify_integrity MUST detect that payload_hash does not match recomputed payload!
        valid_payload_tampered, fail_idx = ledger.verify_integrity()
        self.assertFalse(valid_payload_tampered)
        self.assertEqual(fail_idx, 2)

    def test_merkle_tree_and_cryptographic_witness_receipt(self):
        """
        Test Merkle root derivation and cryptographically signed local HMAC-SHA256 checkpoint witness receipt
        """
        ledger = HashChainedEvidenceLedger()
        for i in range(8):
            ledger.append(
                {"target_endpoint": f"https://updates.vendor.com/v{i}", "vantage_id": "local"},
                violations=[],
                priority=0.05
            )
        root = ledger.compute_merkle_root(1, 8)
        self.assertEqual(len(root), 64)

        receipt = ledger.anchor_witness(1, 8)
        self.assertEqual(receipt["merkle_root"], root)
        self.assertIn("signature_token", receipt)

        # Verify cryptographic signature verification function
        self.assertTrue(ledger.verify_witness_receipt(receipt))

        # Tampered receipt must fail verification
        tampered_receipt = dict(receipt)
        tampered_receipt["merkle_root"] = "0" * 64
        self.assertFalse(ledger.verify_witness_receipt(tampered_receipt))

    def test_bounded_ucb1_guardrails_and_learning(self):
        """Verify UCB1 chooses valid intervals, adapts rewards upon alerts, and enforces budget guardrails"""
        triage = BoundedAITriage()
        # Normal high budget: selects an arm based on UCB
        interval = triage.select_interval(total_budget_remaining_mb=10.0)
        self.assertIn(interval, [10.0, 30.0, 60.0])

        # Exhaust budget < 2.0 MB: must fall back to conservative 60s
        interval_exhausted = triage.select_interval(total_budget_remaining_mb=1.5)
        self.assertEqual(interval_exhausted, 60.0)

        # Update arm rewards and verify statistics change
        initial_pulls = triage.arm_pulls["aggressive_10s"]
        triage.update_arm_reward("aggressive_10s", 1.0)
        self.assertEqual(triage.arm_pulls["aggressive_10s"], initial_pulls + 1)

    def test_rfc8785_canonicalization_compliance(self):
        """Verify RFC 8785 JSON Canonicalization Scheme (JCS) deterministic property sorting, UTF-16 order, safe integers, and float formatting"""
        test_dict = {
            "b": 2,
            "a": 1,
            "neg_zero": -0.0,
            "small_float_exp": 1e-7,
            "small_float_dec_6": 1e-6,
            "small_float_dec_5": 1e-5,
            "large_float_dec_20": 1e20,
            "large_float_exp_21": 1e21,
            "nested": {
                "z": "hello",
                "y": [3, 1, 2],
                "x": True
            },
            "\u00e9": "accent",
            "\uffff": "high_bmp",
            "\U00010000": "supplementary_astral",
            "\U0001f600": "emoji"
        }
        canonical_bytes = canonicalize_jcs(test_dict)
        canonical_str = canonical_bytes.decode('utf-8')
        
        # Verify key ordering: 'a' before 'b', nested properly sorted, UTF-16 code unit order
        self.assertTrue(canonical_bytes.startswith(b'{"a":1,"b":2,'))
        self.assertIn('"neg_zero":0', canonical_str)
        self.assertIn('"small_float_exp":1e-7', canonical_str)
        self.assertIn('"small_float_dec_6":0.000001', canonical_str)
        self.assertIn('"small_float_dec_5":0.00001', canonical_str)
        self.assertIn('"large_float_dec_20":100000000000000000000', canonical_str)
        self.assertIn('"large_float_exp_21":1e+21', canonical_str)
        self.assertIn('"nested":{"x":true,"y":[3,1,2],"z":"hello"}', canonical_str)
        
        # Verify UTF-16 code unit order:
        # In UTF-16, \U00010000 is represented by surrogate pair \uD800\uDC00.
        # Since \uD800 (55296) < \uFFFF (65535), \U00010000 MUST sort BEFORE \uFFFF (RFC 8785 Section 3.2.3)!
        idx_astral = canonical_str.index("\U00010000")
        idx_bmp = canonical_str.index("\uffff")
        self.assertLess(idx_astral, idx_bmp, "RFC 8785 requires UTF-16 code unit ordering where surrogate 0xD800 < 0xFFFF")

        # Verify safe integer validation
        safe_max = 9007199254740991  # 2^53 - 1
        self.assertEqual(canonicalize_jcs(safe_max), b"9007199254740991")
        self.assertEqual(canonicalize_jcs(-safe_max), b"-9007199254740991")
        with self.assertRaises(ValueError):
            canonicalize_jcs(9007199254740993)
        with self.assertRaises(ValueError):
            canonicalize_jcs(-9007199254740993)

        # Verify non-finite numbers rejection
        with self.assertRaises(ValueError):
            canonicalize_jcs(float('nan'))
        with self.assertRaises(ValueError):
            canonicalize_jcs(float('inf'))

if __name__ == '__main__':
    unittest.main()
