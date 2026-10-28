# Reproducibility Guide: FLASHWINDOW Prototype & Benchmarks

This repository contains the complete experimental harness, reference prototype, benchmark evaluation suites, and manuscript generation pipeline for:

**FLASHWINDOW: Temporal Evidence Reconstruction and Adaptive Witnessing for Ephemeral Software-Update Tampering**  
*Target Journal*: ACM Transactions on Privacy and Security (ACM TOPS)

---

## 1. Directory Structure

```
FLASH_WINDOW/
├── benchmark_prototype/              # Modular Python prototype engine
│   ├── __init__.py                   # Package exports
│   └── flashwindow_engine.py         # 4-Layer evidence core & UCB1 bandit
├── experiments/                      # Reproducible experiment runners
│   ├── run_controlled_campaigns.py   # 500 controlled campaigns (5 dwell windows)
│   ├── run_controlled_benign_controls.py # 2,000 benign negative control trials
│   ├── run_split_view_trials.py      # 100 dedicated distributed split-view trials
│   ├── run_real_benchmarks.py        # 1,375 curated proxy telemetry invariant tests
│   ├── run_ablations.py              # 600 paired architectural ablation trials
│   ├── reproduce_all_metrics.py      # Master end-to-end reconciliation verifier
│   └── process_results.py            # Summary JSON generator
├── results/                          # Raw logs and processed experimental summaries
│   ├── raw/                          # JSON trial logs (controlled, benign, split-view, ablations, benchmarks)
│   ├── processed/                    # JSON summary files
│   └── figures/                      # Generated vector publication figures
├── reports/                          # Formal technical audit reports and CSVs
├── tests/                            # Automated unit and integration tests
│   └── test_flashwindow_engine.py    # 10 unit tests covering Invariants INV-01 to INV-05, Merkle anchoring, and RFC 8785 compliance
├── acm_submission_template.docx      # Canonical ACM Word submission style template
├── build_flashwindow_docx.py         # Automated DOCX generator & Word COM PDF exporter
├── verify_flashwindow_checklist.py   # 35-rule ACM TOPS compliance verifier
├── FLASHWINDOW_ACM_TOPS_Revised.docx # Final publication-ready DOCX manuscript
└── FLASHWINDOW_ACM_TOPS_Revised.pdf  # Final publication-ready PDF export
```

---

## 2. Experimental Execution & Verification Workflows

The repository strictly separates: (1) re-running experimental harnesses from scratch, (2) recomputing summary metrics from existing raw execution logs, and (3) running unit, mathematical, and formatting compliance checks.

### Workflow A: Run Automated Verification Suites (Unit Tests, Math, ACM Checklist)
```bash
# 1. Run engine unit tests (INV-01 to INV-05, Merkle anchoring, RFC 8785 canonicalizer)
python -m unittest tests/test_flashwindow_engine.py
# Alternatively: pytest -q tests/test_flashwindow_engine.py

# 2. Verify closed-form analytical equations and probabilistic derivations
python experiments/verify_analytical_math.py

# 3. Verify 35-rule ACM TOPS formatting and structure checklist
python verify_flashwindow_checklist.py
```
*Expected*: 10/10 unit tests pass; 12/12 mathematical verifications pass; 35/35 checklist rules pass (100% ACM compliant).

### Workflow B: Recompute and Reconcile Metrics from Raw Logs
```bash
# Recompute all headline counts, recall, FPR, latency, and Wilson 95% CIs from raw JSONL logs
python experiments/reproduce_all_metrics.py
```
*Generates `results/processed/validated_manuscript_metrics.json` and `results/processed/metrics_reconciliation.csv` directly from raw trial logs.*

### Workflow C: Re-run Underlying Experimental Campaigns from Scratch
```bash
# 1. Run 500 controlled attack campaigns across 5 dwell windows (30s, 60s, 180s, 420s, 900s)
python experiments/run_controlled_campaigns.py

# 2. Run 2,000 negative baseline control trials (with 7 pre-specified challenge conditions)
python experiments/run_controlled_benign_controls.py

# 3. Run 100 dedicated distributed split-view trials (2-round consensus arbitration)
python experiments/run_split_view_trials.py

# 4. Run 600 architectural ablation trials across 6 configurations (with active AI triage measurement)
python experiments/run_ablations.py

# 5. Evaluate 1,375 curated proxy telemetry invariant fixtures across 4 Kaggle suites
python benchmark_prototype/evaluate_real_datasets.py
```

### Workflow D: Rebuild Publication Figures, DOCX Manuscript, and PDF Export
```bash
# 1. Regenerate 300 DPI publication figures (Figures 1-9)
python generate_flashwindow_figures.py

# 2. Build camera-ready DOCX and export PDF
python build_flashwindow_docx.py
```
*Compiles `FLASHWINDOW_ACM_TOPS_Revised.docx` and automatically exports `FLASHWINDOW_ACM_TOPS_Revised.pdf` (via Word COM on Windows or LibreOffice `soffice` on Linux/macOS).*
