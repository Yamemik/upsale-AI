from pathlib import Path
import joblib


class ModelManager:

    MODEL_PATH = Path("models/lightgbm_model.pkl")

    def save(self, model):
        joblib.dump(model, self.MODEL_PATH)

    def load(self):
        return joblib.load(self.MODEL_PATH)
