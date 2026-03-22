"""
Этапы конвейера (соответствие целевой схеме):

[1С:Предприятие]
        │
        ▼
[Выгрузка CSV / OData API]     ← sales import + integration_1c
        │
        ▼
[Загрузка в PostgreSQL]        ← таблицы sales, products, warehouses
        │
        ▼
[Очистка данных]               ← SalesDataCleaningService
(пропуски, выбросы)
        │
        ▼
[Feature Engineering]          ← FeatureEngineeringService
(lag, rolling, календарь, промо)
        │
        ▼
[Обучение модели]              ← LightGBM / CatBoost
(LightGBM / CatBoost)
        │
        ▼
[Оценка качества]              ← mape, rmse
(MAPE, RMSE)
        │
        ▼
[Сохранение модели]            ← ModelManager (.pkl)
(.pkl / .txt)
        │
        ▼
[Прогнозирование]              ← ForecastingService.generate_forecast
        │
        ▼
[Оптимизация запасов]          ← suggested_order_quantity
(расчет заказа)
        │
        ▼
[Отправка в 1С]              ← OneCPushService (REST / OData)
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
    (PipelineStage.ONE_C_SOURCE, "Источник: 1С:Предприятие"),
    (PipelineStage.EXPORT_CSV_ODATA, "Выгрузка CSV или OData API"),
    (PipelineStage.LOAD_POSTGRES, "Загрузка в PostgreSQL"),
    (PipelineStage.DATA_CLEANING, "Очистка данных (пропуски, выбросы)"),
    (PipelineStage.FEATURE_ENGINEERING, "Feature Engineering (lag, rolling, календарь, промо)"),
    (PipelineStage.TRAIN_MODEL, "Обучение модели (LightGBM / CatBoost)"),
    (PipelineStage.EVALUATE, "Оценка качества (MAPE, RMSE)"),
    (PipelineStage.SAVE_MODEL, "Сохранение модели (.pkl)"),
    (PipelineStage.FORECAST, "Прогнозирование"),
    (PipelineStage.INVENTORY_OPTIMIZATION, "Оптимизация запасов (расчёт заказа)"),
    (PipelineStage.PUSH_TO_ONE_C, "Отправка в 1С (REST API / OData)"),
]
