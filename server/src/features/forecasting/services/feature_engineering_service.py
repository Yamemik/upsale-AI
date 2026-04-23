import pandas as pd


class FeatureEngineeringService:
    """Time-series признаки для прогноза продаж на дневном горизонте."""

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        out["sale_date"] = pd.to_datetime(out["sale_date"], errors="coerce")
        out = out.dropna(subset=["sale_date"])
        out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce").fillna(0.0)
        out["price"] = pd.to_numeric(out.get("price", 0.0), errors="coerce").fillna(0.0)

        if "shop_id" not in out.columns:
            out["shop_id"] = 0
        if "item_id" not in out.columns:
            out["item_id"] = 0
        if "item_category_id" not in out.columns:
            out["item_category_id"] = 0

        out["shop_id"] = pd.to_numeric(out["shop_id"], errors="coerce").fillna(0).astype(int)
        out["item_id"] = pd.to_numeric(out["item_id"], errors="coerce").fillna(0).astype(int)
        out["item_category_id"] = (
            pd.to_numeric(out["item_category_id"], errors="coerce").fillna(0).astype(int)
        )

        daily = (
            out.groupby(["shop_id", "item_id", "item_category_id", "sale_date"], as_index=False)
            .agg(
                target_quantity=("quantity", "sum"),
                avg_price=("price", "mean"),
            )
            .sort_values(["shop_id", "item_id", "sale_date"])
            .reset_index(drop=True)
        )

        daily["month"] = daily["sale_date"].dt.month
        daily["day_of_week"] = daily["sale_date"].dt.dayofweek

        grp = daily.groupby(["shop_id", "item_id"], group_keys=False)
        for lag in (1, 7, 14, 28):
            daily[f"lag_{lag}"] = grp["target_quantity"].shift(lag)

        for window in (7, 14, 28):
            daily[f"rolling_mean_{window}"] = (
                grp["target_quantity"]
                .shift(1)
                .rolling(window=window, min_periods=window)
                .mean()
                .reset_index(drop=True)
            )

        daily["price_delta"] = grp["avg_price"].diff()
        daily["price_delta"] = (
            daily["price_delta"].replace([float("inf"), float("-inf")], 0.0).fillna(0.0)
        )

        return daily.dropna().reset_index(drop=True)
