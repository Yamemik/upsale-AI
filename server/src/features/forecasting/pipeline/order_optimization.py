import math


def suggested_order_quantity(
    predicted_monthly_sales: float,
    current_stock: float,
    safety_stock: float = 0.0,
    *,
    lead_time_months: float = 1.0,
    lot_size: float = 1.0,
) -> float:
    """
    Order Quantity = Predicted Monthly Sales * Lead Time - Current Stock + Safety Stock.
    После этого объём заказа округляется вверх до кратности lot_size.
    """
    need = max(
        0.0,
        float(predicted_monthly_sales) * max(0.0, float(lead_time_months))
        - float(current_stock)
        + float(safety_stock),
    )
    if lot_size <= 0:
        lot_size = 1.0
    return math.ceil(need / lot_size) * lot_size
