from fastapi import FastAPI, Depends
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core import logger
import time
from starlette.requests import Request
app = FastAPI()


@app.middleware('http')
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency_ms = round((time.time() - start_time) * 1000, 2)
    logger.info(
        'request',
         extra={
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "latency_ms": latency_ms,
        }

    )
    return response


@app.get('/')
def hello():
    return {'message': "Hello Deepak - What Are We Building Today? "}


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        logger.error("health check failed", extra={"error": str(e)})
        return {"status": "unhealthy"}