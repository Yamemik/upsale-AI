import lightgbm as lgb
import pandas as pd


class LightGBMModel:

    def __init__(self):
        self.model = lgb.LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=8
        )

    def train(self, X: pd.DataFrame, y: pd.Series):
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame):
        return self.model.predict(X)
