from fastapi import APIRouter, HTTPException
from models import FilterRequest, FilterResponse
from screener import (
    filter_by_ema,
    filter_by_rsi,
    filter_by_volume
)

router = APIRouter()

@router.post("/filter", response_model=FilterResponse)
async def filter_endpoint(req: FilterRequest):
    try:
        if req.type == "ema":
            items = await filter_by_ema(
                timeframe=req.timeframe,
                ema_period=req.emaPeriod,
                above=req.emaAbove
            )

        elif req.type == "rsi":
            items = await filter_by_rsi(
                timeframe=req.timeframe,
                period=req.rsiPeriod,
                rsi_min=req.rsiMin,
                rsi_max=req.rsiMax
            )

        elif req.type == "volume":
            items = await filter_by_volume(
                min_v=req.minVolume,
                max_v=req.maxVolume
            )

        else:
            raise HTTPException(400, "Invalid filter type")

        return {"items": items}

    except Exception as e:
        raise HTTPException(500, str(e))
