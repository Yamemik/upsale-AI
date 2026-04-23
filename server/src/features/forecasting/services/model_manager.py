from pathlib import Path
from typing import Any

import joblib
import json


class ModelManager:
    """Версионированное хранение регрессора и метаданных."""

    MODEL_DIR = Path("models")
    REGISTRY_PATH = MODEL_DIR / "registry.json"
    TRAINING_LOG_PATH = MODEL_DIR / "training_events.jsonl"

    def __init__(self) -> None:
        self.MODEL_DIR.mkdir(parents=True, exist_ok=True)
        if not self.REGISTRY_PATH.exists():
            self.REGISTRY_PATH.write_text(
                json.dumps({"latest_version": 0}, ensure_ascii=True, indent=2),
                encoding="utf-8",
            )

    def _read_registry(self) -> dict[str, Any]:
        return json.loads(self.REGISTRY_PATH.read_text(encoding="utf-8"))

    def _write_registry(self, data: dict[str, Any]) -> None:
        self.REGISTRY_PATH.write_text(
            json.dumps(data, ensure_ascii=True, indent=2),
            encoding="utf-8",
        )

    def _model_path(self, version: int) -> Path:
        return self.MODEL_DIR / f"forecast_regressor_v{version}.pkl"

    def get_latest_version(self) -> int:
        data = self._read_registry()
        return int(data.get("latest_version", 0))

    def save(self, payload: dict[str, Any], *, version: int | None = None) -> Path:
        latest = self.get_latest_version()
        target_version = version if version is not None else latest + 1
        path = self._model_path(target_version)
        joblib.dump(payload, path)
        self._write_registry({"latest_version": target_version})
        return path

    def load(self, *, version: int | None = None) -> dict[str, Any]:
        target_version = version if version is not None else self.get_latest_version()
        if target_version <= 0:
            raise FileNotFoundError("Нет сохраненной версии модели")
        return joblib.load(self._model_path(target_version))

    def exists(self) -> bool:
        return self.get_latest_version() > 0 and self._model_path(self.get_latest_version()).is_file()

    def append_training_event(self, payload: dict[str, Any]) -> None:
        with self.TRAINING_LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")
