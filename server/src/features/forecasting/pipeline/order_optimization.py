import math


def suggested_order_quantity(
    forecast_demand: float,
    current_stock: float,
    safety_stock: float = 0.0,
    *,
    lot_size: float = 1.0,
) -> float:
    """
    Рекомендуемый объём заказа: max(0, прогноз + страховой − остаток), с учётом лота.
    """
    need = max(0.0, float(forecast_demand) + float(safety_stock) - float(current_stock))
    if lot_size <= 0:
        lot_size = 1.0
    return math.ceil(need / lot_size) * lot_size
