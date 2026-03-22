import pandas as pd


class FeatureEngineeringService:
    """Lag / rolling / календарь; колонка promo (0/1) — из import_extras или нули."""

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.sort_values("sale_date").reset_index(drop=True)

        if "promo" not in out.columns:
            out["promo"] = 0.0
        out["promo"] = pd.to_numeric(out["promo"], errors="coerce").fillna(0.0)

        out["lag_1"] = out["quantity"].shift(1)
        out["lag_7"] = out["quantity"].shift(7)

        out["rolling_mean_7"] = out["quantity"].rolling(7).mean()
        out["rolling_mean_30"] = out["quantity"].rolling(30).mean()

        out["day_of_week"] = out["sale_date"].dt.dayofweek
        out["month"] = out["sale_date"].dt.month
        out["week"] = out["sale_date"].dt.isocalendar().week.astype(int)

        return out.dropna()
