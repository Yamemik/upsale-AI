from pathlib import Path
from typing import Any

import joblib


class ModelManager:
    """Сохранение обученного регрессора и метаданных (путь к .pkl)."""

    MODEL_DIR = Path("models")
    MODEL_PATH = MODEL_DIR / "forecast_regressor.pkl"

    def __init__(self) -> None:
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)

    def save(self, payload: dict[str, Any]) -> Path:
        joblib.dump(payload, self.MODEL_PATH)
        return self.MODEL_PATH

    def load(self) -> dict[str, Any]:
        return joblib.load(self.MODEL_PATH)

    def exists(self) -> bool:
        return self.MODEL_PATH.is_file()
