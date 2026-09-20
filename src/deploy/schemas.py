"""请求/响应的数据契约（pydantic v2）。非法输入在进模型之前就被 422 拦下。"""

from pydantic import BaseModel, Field

LABELS = ["graphics", "baseball", "hockey", "space"]


class PredictRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=64,
                             examples=[["Looking for a graphics card for ray tracing"]])


class Prediction(BaseModel):
    label: str
    confidence: float
    probabilities: dict[str, float] = {}
    note: str | None = None


class PredictResponse(BaseModel):
    model_version: str
    latency_ms: float
    predictions: list[Prediction]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
