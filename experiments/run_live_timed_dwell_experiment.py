"""
experiments/run_live_timed_dwell_experiment.py
Live Timed Ephemeral Dwell-Window Experiment Harness.

Unlike model-conditioned integration simulations, this harness enacts genuine
wall-clock timed attacks against a live localhost HTTP server:
1. Spawns a real HTTP server serving software update manifests.
2. Attacker thread activates genuine tampering at wall-clock monotonic timestamp t_attack_on.
3. The attack remains active for a live wall-clock dwell window (W in seconds).
4. Attacker reverts the server to authentic state at wall-clock monotonic timestamp t_attack_off.
5. The FlashWindow client daemon probes the server at scheduler-determined intervals.
6. The harness logs high-resolution monotonic timestamps and independently verifies
   whether the prober intercepted the malicious manifest before the attack reverted.

Outputs:
- results/raw/live_timed_dwell_trials.jsonl (per-trial monotonic event logs)
- results/processed/live_timed_dwell_summary.json (empirical wall-clock capture summary)
"""

import os
import sys
import time
import json
import socket
import hashlib
import hmac
import http.server
import threading
import urllib.request
import urllib.error
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from benchmark_prototype.flashwindow_engine import (
    FlashWindowEngine,
    PolicyConfiguration,
    ManifestSnapshot,
    MicroProbeTelemetry,
    AlertSeverity,
    InvariantID
)

RAW_DIR = os.path.join(BASE_DIR, "results", "raw")
PROC_DIR = os.path.join(BASE_DIR, "results", "processed")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROC_DIR, exist_ok=True)

class LiveServerState:
    def __init__(self, key: bytes):
        self.key = key
        self.legit_version = "1.0.0"
        self.legit_url = "https://updates.vendor.com/pkg-1.0.0.bin"
        self.legit_payload = b'{"version":"1.0.0","integrity":"sha256-verified"}'
        self.legit_sha256 = hashlib.sha256(self.legit_payload).hexdigest()
        self.legit_etag = f'"{hashlib.md5(self.legit_payload).hexdigest()[:16]}"'
        self.legit_sig = hmac.new(key, self.legit_sha256.encode('utf-8'), hashlib.sha256).hexdigest()

        # Dynamic live state
        self.is_tampered = False
        self.tamper_lock = threading.Lock()

class LiveHTTPHandler(http.server.BaseHTTPRequestHandler):
    state: LiveServerState = None

    def log_message(self, format, *args):
        pass  # Suppress console HTTP log noise

    def do_HEAD(self):
        with self.state.tamper_lock:
            is_attack = self.state.is_tampered

        etag = '"etag-malicious-tampered"' if is_attack else self.state.legit_etag
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("ETag", etag)
        self.end_headers()

    def do_GET(self):
        with self.state.tamper_lock:
            is_attack = self.state.is_tampered

        if is_attack:
            body = b'{"version":"1.0.0","payload":"MALICIOUS_TROJAN_INJECTED"}'
            sig = "bad_signature_0000"
            url = "http://attacker.com/trojan.bin"
        else:
            body = self.state.legit_payload
            sig = self.state.legit_sig
            url = self.state.legit_url

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("ETag", f'"{hashlib.md5(body).hexdigest()[:16]}"')
        self.send_header("X-Package-Signature", sig)
        self.send_header("X-Download-URL", url)
        self.end_headers()
        self.wfile.write(body)

class AdaptiveLiveScheduler:
    def __init__(self, base_interval: float = 0.35, accelerated_interval: float = 0.15):
        self.base_interval = base_interval
        self.accelerated_interval = accelerated_interval
        self.current_interval = base_interval

    def update(self, signal_changed: bool) -> float:
        if signal_changed:
            self.current_interval = self.accelerated_interval
        else:
            self.current_interval = self.base_interval
        return self.current_interval

def run_live_timed_dwell_experiment(num_trials: int = 12):
    print("=" * 70)
    print("  FLASHWINDOW LIVE TIMED DWELL-WINDOW EMPIRICAL EXPERIMENT")
    print("  (Physically timed attack activation, scheduled probing, and reversion)")
    print("=" * 70)

    vendor_key = b"VENDOR_SECRET_SIGNING_KEY_LIVE"
    state = LiveServerState(vendor_key)
    LiveHTTPHandler.state = state

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), LiveHTTPHandler)
    server_port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    endpoint_url = f"http://127.0.0.1:{server_port}/manifest.json"

    policy = PolicyConfiguration(
        approved_origins={"updates.vendor.com", "cdn.vendor.com"},
        require_https=False,  # Allow localhost testing
        require_signatures=True,
        consensus_threshold=0.67
    )
    engine = FlashWindowEngine(policy)

    # Test dwell durations across short wall-clock intervals (0.5s to 2.5s)
    dwell_durations = [0.5, 0.8, 1.2, 1.8, 2.5]
    trial_records: List[Dict[str, Any]] = []

    raw_path = os.path.join(RAW_DIR, "live_timed_dwell_trials.jsonl")

    with open(raw_path, "w", encoding="utf-8") as raw_f:
        for t_idx in range(num_trials):
            W = dwell_durations[t_idx % len(dwell_durations)]
            state.is_tampered = False

            scheduler = AdaptiveLiveScheduler(base_interval=0.35, accelerated_interval=0.15)
            probe_interval = scheduler.current_interval

            trial_start_mono = time.monotonic()
            # Randomize attack onset between 0.1s and 0.5s after trial start
            onset_delay = 0.1 + (0.05 * (t_idx % 5))
            
            attack_on_mono = None
            attack_off_mono = None
            observed_tamper_mono = None
            detected_violation = None
            probe_log = []

            stop_probe = threading.Event()

            def attacker_routine():
                nonlocal attack_on_mono, attack_off_mono
                time.sleep(onset_delay)
                with state.tamper_lock:
                    state.is_tampered = True
                attack_on_mono = time.monotonic()
                time.sleep(W)
                with state.tamper_lock:
                    state.is_tampered = False
                attack_off_mono = time.monotonic()

            att_thread = threading.Thread(target=attacker_routine)
            att_thread.start()

            # Prober loop
            loop_duration = onset_delay + W + 0.8
            t_end = time.monotonic() + loop_duration
            probe_idx = 0

            while time.monotonic() < t_end:
                probe_idx += 1
                req_start = time.monotonic()
                try:
                    req = urllib.request.Request(endpoint_url, method="GET")
                    with urllib.request.urlopen(req, timeout=1.0) as resp:
                        data = resp.read()
                        etag = resp.headers.get("ETag", "")
                        sig = resp.headers.get("X-Package-Signature", "")
                        d_url = resp.headers.get("X-Download-URL", "")
                    resp_end = time.monotonic()

                    with state.tamper_lock:
                        srv_state_tampered = state.is_tampered

                    # Check if attack was physically active on server during this probe
                    probe_was_during_attack = (
                        attack_on_mono is not None and
                        attack_off_mono is None and
                        req_start >= attack_on_mono
                    ) or (
                        attack_on_mono is not None and
                        attack_off_mono is not None and
                        attack_on_mono <= req_start <= attack_off_mono
                    )

                    # Tier-1 Prober multi-signal drift detection
                    micro = engine.prober.probe(
                        endpoint_url,
                        {"ETag": etag, "status": "200", "latency_ms": str((resp_end - req_start) * 1000.0)},
                        ["127.0.0.1"],
                        "cert_live"
                    )

                    # Adaptive scheduler interval update
                    old_interval = scheduler.current_interval
                    new_interval = scheduler.update(micro.signal_changed)
                    scheduler_updated = (old_interval != new_interval)
                    probe_interval = new_interval

                    # Invariant evaluation
                    snap = ManifestSnapshot(
                        version="1.0.0",
                        download_url=d_url,
                        payload_sha256=hashlib.sha256(data).hexdigest(),
                        signature_present=bool(sig),
                        signature_valid=(sig == state.legit_sig),
                        protocol="http",
                        raw_bytes=data
                    )
                    violations = engine.invariants.verify_manifest(snap, False, 0.0, False, 1.0)
                    is_detected = len(violations) > 0

                    probe_log.append({
                        "probe_index": probe_idx,
                        "request_start_monotonic": round(req_start - trial_start_mono, 4),
                        "response_completion_monotonic": round(resp_end - trial_start_mono, 4),
                        "round_trip_latency_ms": round((resp_end - req_start) * 1000.0, 3),
                        "server_side_state_tampered": srv_state_tampered,
                        "during_attack_window": probe_was_during_attack,
                        "micro_signal_changed": micro.signal_changed,
                        "scheduler_interval_before_sec": round(old_interval, 3),
                        "scheduler_interval_after_sec": round(new_interval, 3),
                        "scheduler_updated": scheduler_updated,
                        "detected_invariants": [v.details for v in violations]
                    })

                    if is_detected and observed_tamper_mono is None:
                        observed_tamper_mono = req_start
                        detected_violation = violations[0].details

                except Exception as e:
                    resp_end = time.monotonic()
                    probe_log.append({
                        "probe_index": probe_idx,
                        "request_start_monotonic": round(req_start - trial_start_mono, 4),
                        "response_completion_monotonic": round(resp_end - trial_start_mono, 4),
                        "error": str(e)
                    })

                time.sleep(probe_interval)

            att_thread.join()

            captured = (
                observed_tamper_mono is not None and
                attack_on_mono is not None and
                attack_off_mono is not None and
                attack_on_mono <= observed_tamper_mono <= (attack_off_mono + 0.05)
            )

            rec = {
                "trial_id": t_idx + 1,
                "dwell_window_seconds": W,
                "onset_delay_seconds": round(onset_delay, 3),
                "attack_on_monotonic": round(attack_on_mono - trial_start_mono, 4) if attack_on_mono else None,
                "attack_off_monotonic": round(attack_off_mono - trial_start_mono, 4) if attack_off_mono else None,
                "actual_active_dwell_seconds": round(attack_off_mono - attack_on_mono, 4) if (attack_on_mono and attack_off_mono) else None,
                "captured_before_reversion": captured,
                "first_detection_monotonic": round(observed_tamper_mono - trial_start_mono, 4) if observed_tamper_mono else None,
                "time_to_detect_seconds": round(observed_tamper_mono - attack_on_mono, 4) if (observed_tamper_mono and attack_on_mono) else None,
                "primary_violation": detected_violation,
                "total_probes_in_trial": len(probe_log),
                "probe_events": probe_log
            }
            raw_f.write(json.dumps(rec) + "\n")
            trial_records.append(rec)
            status_str = "CAPTURED" if captured else "MISSED (Reverted Before Probe)"
            ttd_str = f"{rec['time_to_detect_seconds']:.3f}s" if rec['time_to_detect_seconds'] is not None else "N/A"
            print(f"  Trial {t_idx+1:2d}: Dwell={W:.1f}s | Probes={len(probe_log)} | State={status_str} | TTD={ttd_str}")

    server.shutdown()
    server.server_close()

    total = len(trial_records)
    captures = sum(1 for r in trial_records if r["captured_before_reversion"])
    mean_ttd = sum(r["time_to_detect_seconds"] for r in trial_records if r["time_to_detect_seconds"] is not None) / captures if captures > 0 else 0.0

    summary = {
        "experiment_title": "FLASHWINDOW Live Timed Ephemeral Dwell-Window Empirical Validation",
        "methodology": "Physically timed wall-clock attack activation and restoration with live scheduled probing",
        "total_trials": total,
        "captured_before_reversion": captures,
        "live_timed_capture_rate": round(captures / total, 4),
        "mean_wall_clock_time_to_detect_seconds": round(mean_ttd, 3),
        "raw_records_file": raw_path,
        "provenance": {
            "endpoint": "http://127.0.0.1 (live BaseHTTPRequestHandler)",
            "timing_clock": "time.monotonic() (high-resolution OS monotonic clock)",
            "dwell_durations_tested_seconds": dwell_durations
        }
    }

    sum_path = os.path.join(PROC_DIR, "live_timed_dwell_summary.json")
    with open(sum_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n[+] Live timed dwell experiment complete.")
    print(f"    Total Live Trials: {total} | Captures: {captures} ({captures/total*100:.1f}%)")
    print(f"    Mean Measured Wall-Clock TTD: {mean_ttd:.3f} seconds")
    print(f"    Raw records saved to: {raw_path}")
    print(f"    Canonical summary saved to: {sum_path}")
    print("=" * 70)
    return summary

if __name__ == "__main__":
    run_live_timed_dwell_experiment(12)
