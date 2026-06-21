from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from .config import EnterpriseConfig
from .models import ComparedItem, Severity


def _mad(values: np.ndarray, median: float) -> float:
    return float(np.median(np.abs(values - median)))


def enrich_consensus_anomalies(rows: list[ComparedItem], config: EnterpriseConfig) -> None:
    groups: dict[str, list[ComparedItem]] = defaultdict(list)
    for row in rows:
        groups[row.canonical_id].append(row)

    t = config.thresholds
    for group in groups.values():
        prices = np.asarray([
            r.candidate.unit_price for r in group
            if r.candidate is not None and r.candidate.unit_price is not None and r.candidate.unit_price >= 0
        ], dtype=np.float64)
        if len(prices) < t.min_bidders_for_consensus:
            continue
        median = float(np.median(prices))
        mad = _mad(prices, median)
        scale = 1.4826 * mad
        for row in group:
            row.consensus_price = median
            row.consensus_mad = mad
            price = row.candidate.unit_price if row.candidate else None
            if price is None:
                continue
            if scale > 1e-9:
                z = (price - median) / scale
            elif median != 0:
                z = (price - median) / max(abs(median) * 0.01, 1.0)
            else:
                z = 0.0
            row.robust_z = float(z)
            if abs(z) >= t.robust_z_critical:
                row.flags.append(f"Giá lệch mạnh so với trung vị các HSDT (Robust Z={z:.2f})")
                row.severity = Severity.CRITICAL
                row.anomaly_score = min(100.0, row.anomaly_score + 35)
            elif abs(z) >= t.robust_z_warn:
                row.flags.append(f"Giá khác biệt so với trung vị các HSDT (Robust Z={z:.2f})")
                if row.severity in {Severity.OK, Severity.INFO, Severity.REVIEW}:
                    row.severity = Severity.WARNING
                row.anomaly_score = min(100.0, row.anomaly_score + 20)

    _add_isolation_forest_signal(rows, config)


def _add_isolation_forest_signal(rows: list[ComparedItem], config: EnterpriseConfig) -> None:
    usable: list[ComparedItem] = []
    features: list[list[float]] = []
    for row in rows:
        if not row.candidate or row.candidate.unit_price is None:
            continue
        p_ratio = row.price_delta_pct if row.price_delta_pct is not None else 0.0
        q_ratio = row.quantity_delta_pct if row.quantity_delta_pct is not None else 0.0
        name_gap = 1.0 - row.match.score
        unit_mismatch = 1.0 if row.reference and row.reference.normalized_unit and row.candidate.normalized_unit and row.reference.normalized_unit != row.candidate.normalized_unit else 0.0
        log_price = math.log1p(max(row.candidate.unit_price, 0.0))
        features.append([
            float(np.clip(p_ratio, -10, 10)),
            float(np.clip(q_ratio, -10, 10)),
            name_gap,
            unit_mismatch,
            log_price,
        ])
        usable.append(row)
    if len(features) < 30:
        return
    try:
        from sklearn.ensemble import IsolationForest
        model = IsolationForest(
            n_estimators=200,
            max_samples="auto",
            contamination="auto",
            n_jobs=-1,
            random_state=config.random_state,
        )
        matrix = np.asarray(features, dtype=np.float64)
        model.fit(matrix)
        # Lower decision function is more anomalous. Convert to bounded 0..1 signal.
        decision = model.decision_function(matrix)
        q05, q95 = np.quantile(decision, [0.05, 0.95])
        denom = max(q95 - q05, 1e-9)
        signals = np.clip((q95 - decision) / denom, 0, 1)
        for row, signal in zip(usable, signals):
            if signal >= 0.90:
                row.flags.append(f"Mẫu đa biến bất thường (IsolationForest={signal:.2f})")
                if row.severity in {Severity.OK, Severity.INFO, Severity.REVIEW}:
                    row.severity = Severity.WARNING
                row.anomaly_score = min(100.0, row.anomaly_score + float(signal) * 15)
    except Exception:
        return
