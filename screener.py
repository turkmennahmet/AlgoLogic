from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Literal, Dict
import asyncio

from binance_client import (
    BinanceClient,
    usdt_spot_trading_symbols,
    quote_volume_map_24h,
    closes_from_klines,
    last_close,
)
from indicators import ema_last, rsi_wilder_last

Timeframe = Literal["15m", "1h", "4h", "1d"]
EmaPeriod = Literal[7, 25, 99]

@dataclass
class ResultItem:
    symbol: str
    close: float
    quoteVolume24h: float
    rsi: Optional[float] = None
    ema: Optional[float] = None

async def _symbols_and_volumes(client: BinanceClient) -> tuple[List[str], Dict[str, float]]:
    ex = await client.exchange_info()
    syms = usdt_spot_trading_symbols(ex)

    t24 = await client.ticker_24h_all()
    vol_map = quote_volume_map_24h(t24)

    # Sadece gerçekten tickerdan hacmi olanları tutmak pratik
    syms = [s for s in syms if s in vol_map]
    return syms, vol_map

async def filter_by_volume(min_v: float, max_v: float) -> List[ResultItem]:
    """Senaryo-2: 24h quoteVolume aralığına göre listele."""
    client = BinanceClient()
    syms, vol_map = await _symbols_and_volumes(client)

    items: List[ResultItem] = []
    for s in syms:
        v = vol_map.get(s, 0.0)
        if min_v <= v <= max_v:
            items.append(ResultItem(symbol=s, close=0.0, quoteVolume24h=v))
    # hacme göre sırala (istersen)
    items.sort(key=lambda x: x.quoteVolume24h, reverse=True)
    return items

async def filter_by_rsi(timeframe: Timeframe, rsi_min: float, rsi_max: float, period: int = 14, lookback: int = 200) -> List[ResultItem]:
    """Senaryo-3: RSI aralığına göre listele."""
    client = BinanceClient()
    syms, vol_map = await _symbols_and_volumes(client)

    sem = asyncio.Semaphore(12)

    async def one(sym: str) -> Optional[ResultItem]:
        async with sem:
            try:
                kl = await client.klines(sym, timeframe, limit=lookback)
            except Exception:
                return None
        closes = closes_from_klines(kl)
        r = rsi_wilder_last(closes, period=period)
        if r is None:
            return None
        if not (rsi_min <= r <= rsi_max):
            return None
        return ResultItem(symbol=sym, close=last_close(kl), quoteVolume24h=vol_map.get(sym, 0.0), rsi=r)

    res = await asyncio.gather(*[one(s) for s in syms])
    out = [x for x in res if x is not None]
    out.sort(key=lambda x: x.rsi)  # düşük RSI önce
    return out

async def filter_by_ema(timeframe: Timeframe, ema_period: EmaPeriod, above: bool = True, lookback: int = 200) -> List[ResultItem]:
    """Senaryo-1: Close, EMA(period)'un üstünde/altında olanları listele."""
    client = BinanceClient()
    syms, vol_map = await _symbols_and_volumes(client)

    sem = asyncio.Semaphore(12)

    async def one(sym: str) -> Optional[ResultItem]:
        async with sem:
            try:
                kl = await client.klines(sym, timeframe, limit=lookback)
            except Exception:
                return None
        closes = closes_from_klines(kl)
        e = ema_last(closes, period=int(ema_period))
        if e is None:
            return None
        c = last_close(kl)
        ok = (c > e) if above else (c < e)
        if not ok:
            return None
        return ResultItem(symbol=sym, close=c, quoteVolume24h=vol_map.get(sym, 0.0), ema=e)

    res = await asyncio.gather(*[one(s) for s in syms])
    out = [x for x in res if x is not None]
    # farkı büyükten küçüğe sıralamak istersen:
    out.sort(key=lambda x: (x.close - (x.ema or x.close)), reverse=True)
    return out
