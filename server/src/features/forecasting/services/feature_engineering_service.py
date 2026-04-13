import pandas as pd


class FeatureEngineeringService:
    """Kaggle-oriented monthly features: lag_1/3/12, rolling_mean_3, seasonality."""

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
        if "category_id" not in out.columns:
            out["category_id"] = 0

        out["shop_id"] = pd.to_numeric(out["shop_id"], errors="coerce").fillna(0).astype(int)
        out["item_id"] = pd.to_numeric(out["item_id"], errors="coerce").fillna(0).astype(int)
        out["category_id"] = (
            pd.to_numeric(out["category_id"], errors="coerce").fillna(0).astype(int)
        )

        out["month_start"] = out["sale_date"].dt.to_period("M").dt.to_timestamp()
        monthly = (
            out.groupby(["shop_id", "item_id", "month_start"], as_index=False)
            .agg(
                item_cnt_month=("quantity", "sum"),
                item_price=("price", "mean"),
                category_id=("category_id", "max"),
            )
            .sort_values(["shop_id", "item_id", "month_start"])
            .reset_index(drop=True)
        )

        grp = monthly.groupby(["shop_id", "item_id"], group_keys=False)
        monthly["lag_1"] = grp["item_cnt_month"].shift(1)
        monthly["lag_3"] = grp["item_cnt_month"].shift(3)
        monthly["lag_6"] = grp["item_cnt_month"].shift(6)
        monthly["lag_12"] = grp["item_cnt_month"].shift(12)
        monthly["rolling_mean_3"] = (
            grp["item_cnt_month"].rolling(window=3, min_periods=3).mean().reset_index(drop=True)
        )
        monthly["rolling_mean_6"] = (
            grp["item_cnt_month"].rolling(window=6, min_periods=6).mean().reset_index(drop=True)
        )
        monthly["price_trend"] = grp["item_price"].pct_change().replace([float("inf"), float("-inf")], 0.0)
        monthly["month_num"] = monthly["month_start"].dt.month
        monthly["year"] = monthly["month_start"].dt.year
        monthly["seasonal_flag"] = monthly["month_num"].isin([12, 1, 2, 6, 7, 8]).astype(int)

        return monthly.dropna().reset_index(drop=True)
