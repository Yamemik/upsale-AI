"""
Этапы конвейера (соответствие целевой схеме):

[Kaggle Dataset]
sales_train.csv, items.csv, shops.csv
        │
        ▼
[Загрузка CSV в систему]          ← Pandas / PostgreSQL
        │
        ▼
[Предобработка данных]            ← удаление выбросов и пропусков
        │
        ▼
[Агрегация]                       ← дневные -> месячные продажи
        │
        ▼
[Feature Engineering]          ← FeatureEngineeringService
(lag_1, lag_3, lag_12, rolling_mean, seasonality)
        │
        ▼
[Обучение модели]              ← LightGBM / CatBoost
        │
        ▼
[Оценка качества]              ← RMSE (стандарт Kaggle)
        │
        ▼
[Сохранение модели]            ← ModelManager (.pkl)
        │
        ▼
[Прогнозирование]              ← test.csv -> item_cnt_month
        │
        ▼
[Оптимизация запасов]          ← формула с lead time
        │
        ▼
[Интеграция с 1С]               ← REST API
"""

from enum import Enum


class PipelineStage(str, Enum):
    ONE_C_SOURCE = "1c_enterprise"
    EXPORT_CSV_ODATA = "export_csv_odata"
    LOAD_POSTGRES = "load_postgresql"
    DATA_CLEANING = "data_cleaning"
    FEATURE_ENGINEERING = "feature_engineering"
    TRAIN_MODEL = "train_model"
    EVALUATE = "evaluate_quality"
    SAVE_MODEL = "save_model"
    FORECAST = "forecast"
    INVENTORY_OPTIMIZATION = "inventory_optimization"
    PUSH_TO_ONE_C = "push_to_1c"


PIPELINE_DESCRIPTION: list[tuple[PipelineStage, str]] = [
    (PipelineStage.ONE_C_SOURCE, "Источник: Kaggle dataset / 1С"),
    (PipelineStage.EXPORT_CSV_ODATA, "Загрузка CSV и справочников"),
    (PipelineStage.LOAD_POSTGRES, "Сохранение в PostgreSQL"),
    (PipelineStage.DATA_CLEANING, "Очистка данных (пропуски, price < 0, выбросы)"),
    (PipelineStage.FEATURE_ENGINEERING, "Feature Engineering (lag_1/3/12, rolling_mean_3, seasonality)"),
    (PipelineStage.TRAIN_MODEL, "Обучение модели (LightGBM / CatBoost)"),
    (PipelineStage.EVALUATE, "Оценка качества (RMSE)"),
    (PipelineStage.SAVE_MODEL, "Сохранение модели (.pkl)"),
    (PipelineStage.FORECAST, "Прогнозирование"),
    (PipelineStage.INVENTORY_OPTIMIZATION, "Оптимизация запасов (lead time, safety stock)"),
    (PipelineStage.PUSH_TO_ONE_C, "Отправка в 1С (REST API / OData)"),
]
