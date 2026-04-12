import numpy as np
import pandas as pd


class SalesDataCleaningService:
    """Очистка продаж под Kaggle-пайплайн (пропуски, отрицательная цена, выбросы)."""

    def __init__(
        self,
        *,
        outlier_iqr_factor: float = 1.5,
        min_quantity: float = 0.0,
    ):
        self.outlier_iqr_factor = outlier_iqr_factor
        self.min_quantity = min_quantity

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        out = out.sort_values("sale_date").reset_index(drop=True)

        if "quantity" not in out.columns:
            raise ValueError("DataFrame must contain 'quantity'")

        out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
        out = out.dropna(subset=["quantity"])
        out = out[out["quantity"] >= self.min_quantity]

        if "price" in out.columns:
            out["price"] = pd.to_numeric(out["price"], errors="coerce")
            out = out[out["price"] >= 0]
            out["price"] = out["price"].ffill().bfill()
        else:
            out["price"] = 0.0

        q = out["quantity"].astype(float)
        if len(q) >= 5:
            q1, q3 = q.quantile(0.25), q.quantile(0.75)
            iqr = q3 - q1
            lo = q1 - self.outlier_iqr_factor * iqr
            hi = q3 + self.outlier_iqr_factor * iqr
            out["quantity"] = np.clip(out["quantity"], lo, hi)

        return out.reset_index(drop=True)
