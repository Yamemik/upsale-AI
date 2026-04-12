"""SHAP-объяснения для tree-моделей (LightGBM / CatBoost sklearn API)."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
import shap

logger = logging.getLogger(__name__)


def tree_shap_contributions(
    model: Any,
    X: pd.DataFrame,
    *,
    max_features: int = 25,
) -> tuple[list[dict[str, Any]], float | None]:
    """
    Возвращает вклад признаков для первой строки X и базовое ожидание модели.
    Каждый элемент: feature_name, feature_value, shap_value.
    """
    if X.empty:
        return [], None

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    ev = explainer.expected_value
    if ev is None:
        base: float | None = None
    else:
        ev_arr = np.asarray(ev).ravel()
        base = float(ev_arr[0]) if ev_arr.size else None

    sv = np.asarray(shap_values)
    if sv.ndim == 0:
        return [], base
    if sv.ndim == 1:
        sv_row = sv
    else:
        sv_row = sv[0]

    row = X.iloc[0]
    names = list(X.columns)
    out: list[dict[str, Any]] = []
    for i, name in enumerate(names):
        if i >= len(sv_row):
            break
        raw = row[name] if name in row.index else None
        try:
            fv = float(raw) if raw is not None and not (isinstance(raw, float) and np.isnan(raw)) else None
        except (TypeError, ValueError):
            fv = None
        out.append(
            {
                "feature_name": str(name),
                "feature_value": fv,
                "shap_value": float(sv_row[i]),
            }
        )

    out.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    return out[:max_features], base
