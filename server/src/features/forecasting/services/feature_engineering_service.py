import pandas as pd


class FeatureEngineeringService:

    def create_features(self, df: pd.DataFrame):

        df["lag_1"] = df["quantity"].shift(1)
        df["lag_7"] = df["quantity"].shift(7)

        df["rolling_mean_7"] = df["quantity"].rolling(7).mean()
        df["rolling_mean_30"] = df["quantity"].rolling(30).mean()

        df["day_of_week"] = df["sale_date"].dt.dayofweek
        df["month"] = df["sale_date"].dt.month

        return df.dropna()
