from __future__ import annotations
from typing import List, Optional

def ema_last(values: List[float], period: int) -> Optional[float]:
    """EMA'nin son değerini döndürür."""
    if len(values) < period or period <= 0:
        return None

    k = 2 / (period + 1)
    # ilk EMA = ilk period SMA
    ema_val = sum(values[:period]) / period
    for v in values[period:]:
        ema_val = (v - ema_val) * k + ema_val
    return float(ema_val)

from typing import List, Optional

def rsi_wilder_last(closes: List[float], period: int) -> Optional[float]:
    """Wilder RSI'nin son değerini döndürür."""
    if period not in (6, 12, 24):
        raise ValueError("RSI period sadece 6, 12 veya 24 olabilir.")
    if len(closes) < period + 1:
        return None

    gains = 0.0
    losses = 0.0
    for i in range(1, period + 1):
        diff = closes[i] - closes[i - 1]
        gains += max(diff, 0.0)
        losses += max(-diff, 0.0)

    avg_gain = gains / period
    avg_loss = losses / period

    for i in range(period + 1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gain = max(diff, 0.0)
        loss = max(-diff, 0.0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return float(100 - (100 / (1 + rs)))

