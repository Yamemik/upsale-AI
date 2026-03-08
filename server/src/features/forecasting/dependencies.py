from src.features.forecasting.services.forecasting_service import ForecastingService


def get_forecast_service() -> ForecastingService:
    return ForecastingService()