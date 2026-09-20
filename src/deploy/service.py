"""FastAPI 推理服务：/healthz 存活、/ready 就绪、/v1/classify 批量预测、可选 Bearer 鉴权。"""

import json
import logging
import secrets
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .inference import Classifier
from .schemas import HealthResponse, PredictRequest, PredictResponse


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"ts": self.formatTime(record), "level": record.levelname,
                   "logger": record.name, "msg": record.getMessage()}
        if hasattr(record, "extra_fields"):
            payload.update(record.extra_fields)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.clf = Classifier.from_path(settings.model_path, min_len=settings.min_text_len)
    app.state.started_at = time.time()
    logging.getLogger("deploy").info("model loaded: %s", settings.model_path)
    yield
    logging.getLogger("deploy").info("shutdown")


app = FastAPI(title="news-text-classifier", lifespan=lifespan)

OPEN_PATHS = {"/healthz", "/ready", "/docs", "/openapi.json"}


@app.middleware("http")
async def bearer_auth(request: Request, call_next):
    token = get_settings().api_token
    if token and request.url.path not in OPEN_PATHS:
        given = request.headers.get("authorization", "")
        if not secrets.compare_digest(given, f"Bearer {token}"):
            return JSONResponse(status_code=401, content={"detail": "unauthorized"})
    return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    dt = (time.perf_counter() - t0) * 1000
    log = logging.getLogger("deploy.access")
    fields = {"path": request.url.path, "method": request.method,
              "status": response.status_code, "latency_ms": round(dt, 1)}
    record = log.makeRecord("deploy.access", logging.INFO, "", 0, "request", (), None)
    record.extra_fields = fields  # type: ignore[attr-defined]
    log.handle(record)
    return response


@app.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=hasattr(app.state, "clf"))


@app.get("/ready", response_model=HealthResponse)
async def ready() -> HealthResponse:
    loaded = hasattr(app.state, "clf")
    return HealthResponse(status="ready" if loaded else "loading", model_loaded=loaded)


@app.post("/v1/classify", response_model=PredictResponse)
async def classify(req: PredictRequest) -> PredictResponse:
    settings = get_settings()
    t0 = time.perf_counter()
    preds = app.state.clf.predict_many(req.texts)
    return PredictResponse(
        model_version=settings.version,
        latency_ms=round((time.perf_counter() - t0) * 1000, 2),
        predictions=preds,
    )
