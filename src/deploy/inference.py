"""模型加载与推理封装：进程内只 load 一次；第3课的长度护栏在这里落地。"""

import joblib
import numpy as np

from .schemas import LABELS, Prediction


class Classifier:
    def __init__(self, pipeline, min_len: int = 10):
        self._pipe = pipeline
        self._min_len = min_len

    @classmethod
    def from_path(cls, path, min_len: int = 10) -> "Classifier":
        return cls(joblib.load(path), min_len=min_len)

    def predict_one(self, text: str) -> Prediction:
        stripped = text.strip()
        if len(stripped) < self._min_len:
            # 护栏：<10词的帖准确率仅52%，拒答好过自信地答错（第3课误差分片结论）
            return Prediction(label="rejected", confidence=0.0, probabilities={},
                              note=f"text shorter than {self._min_len} chars")
        proba = self._pipe.predict_proba([stripped])[0]
        best = int(np.argmax(proba))
        return Prediction(
            label=LABELS[best],
            confidence=round(float(proba[best]), 4),
            probabilities={lbl: round(float(p), 4) for lbl, p in zip(LABELS, proba)},
        )

    def predict_many(self, texts: list[str]) -> list[Prediction]:
        return [self.predict_one(t) for t in texts]
