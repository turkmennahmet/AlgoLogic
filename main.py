from fastapi import FastAPI
from api import router

app = FastAPI(title="AlgoLogic Worker")

app.include_router(router, prefix="/api")

# SADECE servis başlatma
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
