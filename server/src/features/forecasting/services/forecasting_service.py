import pandas as pd

from ..ml.lightgbm_model import LightGBMModel
from .feature_engineering_service import FeatureEngineeringService


class ForecastingService:

    def __init__(self):
        self.model = LightGBMModel()
        self.feature_service = FeatureEngineeringService()

    def train(self, df: pd.DataFrame):

        df = self.feature_service.create_features(df)

        X = df.drop(columns=["quantity", "sale_date"])
        y = df["quantity"]

        self.model.train(X, y)

    def forecast(self, df: pd.DataFrame):

        df = self.feature_service.create_features(df)

        X = df.drop(columns=["quantity", "sale_date"])

        predictions = self.model.predict(X)

        return predictions
