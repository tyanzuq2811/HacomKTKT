from __future__ import annotations

from statistics import mean, median

from .schemas import PriceReference, PriceStats


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("empty values")
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def compute_price_stats(refs: list[PriceReference]) -> PriceStats:
    prices = sorted(float(ref.price) for ref in refs if ref.price > 0)
    if not prices:
        raise ValueError("No positive reference prices")
    return PriceStats(
        count=len(prices),
        min_price=min(prices),
        max_price=max(prices),
        median_price=float(median(prices)),
        mean_price=float(mean(prices)),
        q1_price=_quantile(prices, 0.25),
        q3_price=_quantile(prices, 0.75),
    )


def clamp_price_range(
    low: int,
    high: int,
    stats: PriceStats,
    *,
    max_expansion: float = 0.05,
) -> tuple[int, int, list[str]]:
    warnings: list[str] = []
    
    # Tính toán độ biến động giá tương đối (spread)
    if stats.mean_price > 0:
        spread = (stats.max_price - stats.min_price) / stats.mean_price
        # Dung sai động tỷ lệ thuận với độ biến động, dao động từ 5% đến 25%
        dynamic_expansion = max(0.05, min(0.25, spread * 0.20))
    else:
        dynamic_expansion = max_expansion

    min_allowed = int(round(stats.min_price * (1 - dynamic_expansion)))
    max_allowed = int(round(stats.max_price * (1 + dynamic_expansion)))
    clamped_low = max(min(low, max_allowed), min_allowed)
    clamped_high = max(min(high, max_allowed), min_allowed)
    if clamped_low > clamped_high:
        clamped_low, clamped_high = clamped_high, clamped_low
    if (clamped_low, clamped_high) != (low, high):
        warnings.append(
            f"Khoảng giá LLM đã được ép về biên dữ liệu RAG thích ứng {dynamic_expansion*100:.1f}% ({min_allowed:,}-{max_allowed:,} VND)."
        )
    return clamped_low, clamped_high, warnings

