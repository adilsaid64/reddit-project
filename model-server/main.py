import time
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import generate_latest, Counter, Histogram
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import uvicorn

PREDICTION_REQUESTS = Counter("prediction_requests_total", "Total number of prediction requests")
PREDICTION_ERRORS = Counter("prediction_errors_total", "Total number of failed prediction requests")
PREDICTION_LATENCY = Histogram("prediction_latency_seconds", "Prediction latency in seconds")

logger = logging.getLogger("uvicorn")

ANALYZER: SentimentIntensityAnalyzer | None = None

class GetInferenceRequest(BaseModel):
    text: str

class LabelScore(BaseModel):
    label: str
    score: float

class GetInferenceResponse(BaseModel):
    inference: List[LabelScore]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ANALYZER
    logger.info("Initializing VADER sentiment analyzer")
    ANALYZER = SentimentIntensityAnalyzer()
    logger.info("Analyzer ready")
    yield

app = FastAPI(title="Model Server", description="Simple Sentiment Prediction API", lifespan=lifespan)

@app.post("/get-inference", response_model=GetInferenceResponse)
async def get_inference(payload: GetInferenceRequest) -> GetInferenceResponse:
    start_time = time.time()
    PREDICTION_REQUESTS.inc()

    try:
        assert ANALYZER is not None, "Sentiment analyzer not initialized"
        scores = ANALYZER.polarity_scores(payload.text)
        label = "POSITIVE" if scores["compound"] >= 0 else "NEGATIVE"
        score = max(scores["pos"], scores["neg"])
        prediction = [{"label": label, "score": float(score)}]
        return GetInferenceResponse(inference=prediction)

    except Exception:
        PREDICTION_ERRORS.inc()
        raise
    finally:
        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
