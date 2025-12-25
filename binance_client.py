from __future__ import annotations
from typing import Dict, List, Tuple
import httpx

BINANCE_BASE = "https://api.binance.com"

class BinanceClient:
    def __init__(self, base_url: str = BINANCE_BASE) -> None:
        self.base_url = base_url.rstrip("/")

    async def exchange_info(self) -> dict:
        url = f"{self.base_url}/api/v3/exchangeInfo"
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(url)
            r.raise_for_status()
            return r.json()

    async def ticker_24h_all(self) -> List[dict]:
        url = f"{self.base_url}/api/v3/ticker/24hr"
        async with httpx.AsyncClient(timeout=25) as c:
            r = await c.get(url)
            r.raise_for_status()
            return r.json()

    async def klines(self, symbol: str, interval: str, limit: int = 200) -> List[list]:
        url = f"{self.base_url}/api/v3/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        async with httpx.AsyncClient(timeout=25) as c:
            r = await c.get(url, params=params)
            r.raise_for_status()
            return r.json()


def usdt_spot_trading_symbols(exchange_info: dict) -> List[str]:
    out: List[str] = []
    for s in exchange_info.get("symbols", []):
        if s.get("status") != "TRADING":
            continue
        if s.get("quoteAsset") != "USDT":
            continue
        if s.get("isSpotTradingAllowed") is False:
            continue
        sym = s.get("symbol")
        if sym:
            out.append(sym)
    return out


def quote_volume_map_24h(ticker_24h: List[dict]) -> Dict[str, float]:
    m: Dict[str, float] = {}
    for t in ticker_24h:
        sym = t.get("symbol")
        qv = t.get("quoteVolume")
        if not sym or qv is None:
            continue
        try:
            m[sym] = float(qv)  # 24h quoteVolume (USDT)
        except ValueError:
            pass
    return m


def closes_from_klines(klines: List[list]) -> List[float]:
    return [float(k[4]) for k in klines]  # close


def last_close(klines: List[list]) -> float:
    return float(klines[-1][4])
