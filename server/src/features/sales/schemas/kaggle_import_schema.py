from __future__ import annotations

from pydantic import BaseModel


class KaggleImportStepResult(BaseModel):
    step: str
    title: str
    rows_read: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = []


class KaggleImportRunResult(BaseModel):
    mode: str
    dry_run: bool
    steps_requested: list[str]
    steps_executed: list[KaggleImportStepResult]
    totals: dict[str, int]

