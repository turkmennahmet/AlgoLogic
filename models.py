from pydantic import BaseModel
from typing import Optional, List

class FilterRequest(BaseModel):
    type: str

    timeframe: Optional[str] = None

    # EMA
    emaPeriod: Optional[int] = None
    emaAbove: Optional[bool] = None

    # RSI
    rsiPeriod: Optional[int] = None
    rsiMin: Optional[float] = None
    rsiMax: Optional[float] = None

    # Volume
    minVolume: Optional[float] = None
    maxVolume: Optional[float] = None


class FilterItem(BaseModel):
    symbol: str
    close: float
    quoteVolume24h: float
    rsi: Optional[float] = None
    ema: Optional[float] = None


class FilterResponse(BaseModel):
    items: List[FilterItem]
