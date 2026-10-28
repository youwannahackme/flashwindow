# FLASHWINDOW Research Artifact Repository
**Temporal Evidence Reconstruction and Adaptive Witnessing for Ephemeral Software-Update Tampering**

*Authors: Shoaib Arshad\*, Saba Firdous, Zunair-Ul-Abiden*  
*Department of Computing, Riphah International University, Faisalabad, Pakistan*  
*Target Venue: ACM Transactions on Privacy and Security (ACM TOPS)*

[![ACM Master Checklist](https://img.shields.io/badge/ACM%20TOPS%20Checklist-100%25%20PASS%20(35%2F35)-success)](#acm-compliance-verification)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-10%2F10%20PASS-success)](#unit-testing)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](requirements.txt)

---

## 1. Overview and Problem Statement

**FLASHWINDOW** is an external temporal monitoring, evidence reconstruction, and cryptographic witnessing architecture designed to detect transient, short-lived software supply chain tampering targeting update distribution infrastructure.

Traditional point-in-time vulnerability scanners and host auditing agents (e.g., Osquery, Zeek) exhibit an acute **temporal visibility gap** when sophisticated adversaries execute attacks during narrow dwell windows ($W \in [30\text{s}, 15\text{m}]$) and revert the distribution server to legitimate state before scheduled audits. 

FLASHWINDOW addresses this vulnerability without requiring modifications to legacy client updaters (CWE-494) by synthesizing:
1. **Tier-1 Lightweight Micro-Probing**: ETag, Last-Modified, DNS Anycast, and TLS fingerprint heuristics.
2. **Poisson Background Sampling & Temporal State Machine**: Continuous stochastic monitoring that exposes ephemeral $A \to B \to A$ regressions.
3. **Multi-Vantage Consensus**: Distributed cross-verification across geographically separated nodes to detect targeted split-views.
4. **Deterministic Invariant Engine**: Strict verification of non-negotiable formal invariants (INV-01 through INV-05).
5. **Bounded AI Assistance Plane**: Contextual-bandit rate scheduling (UCB1) with deterministic non-suppression boundaries.
6. **Tamper-Evident Evidence Ledger**: SHA-256 hash chaining anchored by local HMAC-SHA256 checkpoint witness receipts (F-05).

---

## 2. Repository Structure

```
FLASH_WINDOW/
├── README.md                                  # Master reproducibility guide (this file)
├── LICENSE                                    # Apache 2.0 Open Source License
├── CITATION.cff                               # Citation metadata format
├── requirements.txt                           # Python environment dependencies
│
├── FLASHWINDOW_ACM_TOPS_Revised.docx          # Primary Revised ACM Word Manuscript
├── FLASHWINDOW_ACM_TOPS_Revised.pdf           # Primary Revised ACM PDF Manuscript
├── FlashWindow_Research_Paper.md              # Synchronized Markdown Manuscript
│
├── reports/                                   # Formal ACM TOPS Audit Reports (Phases 1-15)
│   ├── initial_audit.md                       # Phase 1: Manuscript Discovery & Defect Audit
│   ├── claim_evidence_matrix.csv              # Phase 2: Claim-to-Evidence Matrix (Categories A-F)
│   ├── novelty_audit.md                       # Phase 3: Intellectual Novelty & Related Work Audit
│   ├── reference_verification.csv             # Phase 3: All 85 Authentic Citations Audited
│   ├── related_work_matrix.csv                # Phase 3: Comparative SOTA Capability Matrix
│   ├── threat_model_review.md                 # Phase 4: Adversary Models & Security Properties
│   ├── mathematical_audit.md                  # Phase 5: Equation Validation & Proposition Proofs
│   ├── dataset_audit.csv                      # Phase 7: Dataset Provenance, URLs & Labels
│   ├── final_review.md                        # Phase 15: Project Internal Quality Audit Memo
│   ├── CHANGELOG.md                           # Master Technical & Structural Change Log
│   └── unresolved_issues.md                   # Researcher Actions Prior to Journal Submission
│
├── benchmark_prototype/                       # Reference Prototype Implementation
│   ├── flashwindow_engine.py                  # Core 4-Layer Python Reference Engine
│   ├── evaluate_real_datasets.py              # Kaggle 1,375-trial benchmark harness
│   ├── real_benchmark_results.json            # Machine-readable trial results log
│   ├── REAL_BENCHMARK_REPORT.md               # Empirical evaluation report
│   └── datasets/                              # Curated Kaggle security corpora
│       ├── README.md                          # Dataset provenance, URLs & labeling
│       ├── checksums.txt                      # Cryptographic SHA-256 hashes
│       ├── supply_chain_risk_graph/           # Suite 1: Package risk snapshots (274 packages)
│       ├── fastflux_dns_telemetry/            # Suite 2: Fast-flux DiG traces (100 trials)
│       ├── oss_vulnerabilities_cve/           # Suite 3: CVE vulnerability records (300 trials)
│       └── lotl_apt_payloads/                 # Suite 4: Real LOTL APT commands (701 trials)
│
├── tests/                                     # Automated Unit & Integration Tests
│   └── test_flashwindow_engine.py             # 10/10 automated unit tests (JCS, Invariants, Ledger)
│
├── experiments/                               # Controlled Experiment Harnesses
│   ├── run_controlled_campaigns.py            # 500 model-conditioned campaigns (W in {30,60,180,420,900}s)
│   ├── run_controlled_benign_controls.py      # 2,000 benign control trials (including 7 challenge cases)
│   ├── run_split_view_trials.py               # 100 dedicated split-view consensus simulation trials
│   ├── run_ablations.py                       # 6 architectural component configurations (600 trials)
│   ├── verify_analytical_math.py              # Analytical mathematical verifier (Equations 1-7)
│   └── reproduce_all_metrics.py               # Master metric reconciliation and receipt verifier
│
├── results/                                   # Experimental Outputs
│   ├── raw/                                   # Original execution logs (.jsonl)
│   │   ├── controlled_campaigns.jsonl         # 500 controlled raw trial records
│   │   ├── controlled_benign_controls.jsonl   # 2,000 benign baseline control records
│   │   ├── split_view_trials.jsonl            # 100 dedicated split-view simulation records
│   │   ├── ablation_trials.jsonl              # 600 ablation trial records
│   │   ├── real_benchmark_eval.jsonl          # 1,375 curated proxy invariant records
│   │   └── witness_receipts.jsonl             # 815 persisted local HMAC witness receipts
│   ├── processed/                             # Derived statistical tables
│   │   ├── controlled_summary.json            # Per-dwell breakdown and split-view metrics
│   │   ├── benchmark_summary.json             # Proxy benchmark metrics with Wilson 95% CIs
│   │   ├── ablation_summary.json              # Ablation trade-offs (recall, FPR, latency)
│   │   ├── validated_manuscript_metrics.json  # Canonical master reconciled metrics JSON
│   │   └── metrics_reconciliation.csv         # Reconciled metrics comparison table
│   └── figures/                               # Processed publication figures (Fig 1-9)
│
└── figures/                                   # Publication Figures Directory
    ├── cropped_png/                           # 300 DPI tightly cropped PNGs
    ├── png/                                   # High-resolution raw PNGs
    └── svg/                                   # Scalable Vector Graphics sources
```

---

## 3. Quick Start & Reproduction Guide

### 3.1 Environment Setup
```bash
# Note: For artifact review, all code, datasets, and scripts are self-contained in this archive.
# The public repository (https://github.com/flashwindow-core/flashwindow) is scheduled for activation upon publication.

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3.2 Run Unit Tests
```bash
pytest -q tests/test_flashwindow_engine.py
```
*Expected Output:* `10 passed in 0.10s`

### 3.3 Execute All Experiments (3,975 Primary Evaluations / 4,575 Total Evaluations)
```bash
# 1. Run live timed dwell experiment (monotonic wall-clock activation and restoration)
python experiments/run_live_timed_dwell_experiment.py

# 2. Run empirical daemon resource overhead measurement (CPU, RSS, loopback TLS)
python benchmark_prototype/measure_resource_overhead.py

# 3. Run 500 model-conditioned controlled campaigns across 5 dwell durations
python experiments/run_controlled_campaigns.py

# 4. Run 2,000 benign baseline controls (including 7 protocol challenge cases)
python experiments/run_controlled_benign_controls.py

# 5. Run 100 dedicated split-view consensus simulation trials across 5 logical vantages
python experiments/run_split_view_trials.py

# 6. Run 1,375 dataset-derived proxy invariant benchmark trials across 4 curated suites
python benchmark_prototype/evaluate_real_datasets.py

# 7. Run component ablation study across 6 architectural configurations (600 trials)
python experiments/run_ablations.py

# 8. Verify analytical mathematical formulations (Equations 1-7)
python experiments/verify_analytical_math.py

# 9. Reproduce and verify all metrics, confidence intervals, and 815 witness receipts
python experiments/reproduce_all_metrics.py
```

## 4. Summary of Validated Empirical Findings

| Evaluation Dimension | Stated Claim in Paper | Empirical Evidence Source | Verified Confidence Bound (95% Wilson Score CI) |
| :--- | :--- | :--- | :--- |
| **Model-Conditioned Controlled Recall (F-01)** | 98.4% Recall | 500 model-conditioned integration campaigns ($W \in [30\text{s}, 900\text{s}]$) | 492/500 captured: $[96.87\%, 99.19\%]$ (Wilson 95% CI) |
| **Benign Challenge Alert Rate (F-04)** | 0.35% Alert Rate | 2,000 randomized benign monitoring controls | 7/2,000 alerts (preselected challenge cases): $[0.17\%, 0.72\%]$; 0 false alarms on 1,993 compliant controls |
| **Curated Proxy Invariant Recall (F-03, F-05)** | 100.0% Fixture Coverage | 1,375 curated proxy fixtures across 4 corpora | 834/834 TPs: $[99.54\%, 100.00\%]$ (Wilson 95% CI; Layer 3 policy rules) |
| **Curated Proxy Invariant FPR (F-03, F-05)** | 0.00% FPR | Negative controls across package registries & CVEs | 0/541 FPs: $[0.00\%, 0.71\%]$ (Wilson 95% CI) |
| **Total Evaluation Scale (F-12)** | Comprehensive Scale | 500 controlled + 2,000 benign + 100 split-view + 1,375 proxy | 3,975 primary evaluations (4,575 total evaluations including 600 ablations) |
| **Bandwidth Reduction (F-08)** | 93.5% Wire / 93.6% Cached | 1.84 MB/day vs. 28.8 MB/day ($T=10\text{m}$ polling) | $93.5\%$ wire / $93.6\%$ cached vs $T=10\text{m}$; $90.4\%$ vs $T=15\text{m}$; $96.8\%$ vs $T=5\text{m}$ |
| **Processing Latency (F-09)** | 0.45 ms Median / 2.68 ms P99 | Prototype in-memory: P50 = 0.45 ms, Mean = 0.62 ms, P95 = 1.34 ms, P99 = 2.68 ms | TLS mediation under stress: P95 = 4.80 ms |
| **Split-View Consensus (F-02, F-04)** | 99.0% 2-Round Consensus | 100 dedicated trials across 5 logical vantages | 99/100: $[94.55\%, 99.82\%]$ (mean modeled arbitration latency 1.50 s) |
| **Ledger & Witness Integrity (F-05, F-07, F-14)**| 100% Immutability | 1,375 unbroken sequential SHA-256 records, 815 signed HMAC receipts | 815/815 local HMAC receipts cryptographically verified via `verify_witness_receipt()` |

---

## 5. Citation

```bibtex
@article{arshad2026flashwindow,
  author    = {Shoaib Arshad and Saba Firdous and Zunair-Ul-Abiden and Talha Ahsan},
  title     = {FLASHWINDOW: Temporal Evidence Reconstruction and Adaptive Witnessing for Ephemeral Software-Update Tampering},
  journal   = {ACM Transactions on Privacy and Security},
  year      = {2026},
  publisher = {Association for Computing Machinery},
  address   = {New York, NY, USA}
}
```

---

## 6. License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
