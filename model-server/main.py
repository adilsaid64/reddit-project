import time
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging
from fastapi.responses import Response
from prometheus_client import generate_latest, Counter, Histogram
from transformers import pipeline
import uvicorn

PREDICTION_REQUESTS = Counter("prediction_requests_total", "Total number of prediction requests")
PREDICTION_ERRORS = Counter("prediction_errors_total", "Total number of failed prediction requests")
PREDICTION_LATENCY = Histogram("prediction_latency_seconds", "Prediction latency in seconds")

logger = logging.getLogger("uvicorn")

MODEL = None

class GetInferenceRequest(BaseModel):
    """Get Prediction Payload"""
    text: str

class GetInferenceResponse(BaseModel):
    """Get Prediction Response"""
    inference: dict[str, str]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler"""
    global MODEL
    logger.info("Loading Model")
    MODEL = pipeline("sentiment-analysis")
    logger.info(f"Model Loaded")
    yield

app = FastAPI(title="Model Server", description="Sentiment Prediction API", lifespan=lifespan)

@app.post("/get-inference")
async def get_inference(payload: GetInferenceRequest) -> GetInferenceResponse:
    """Return Model Inference"""
    start_time = time.time()
    PREDICTION_REQUESTS.inc()

    try:
        prediction = MODEL(payload.text)
        return GetInferenceResponse(inference=prediction)
    
    except Exception as e:
        PREDICTION_ERRORS.inc()
        raise e

    finally:
        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )