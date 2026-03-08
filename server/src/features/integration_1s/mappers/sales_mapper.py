from src.features.sales.models.sale_model import Sale


def map_sale(onec_data: dict) -> Sale:

    return Sale(
        product_id=onec_data["Номенклатура_Key"],
        product_name=onec_data["Номенклатура"],
        sale_date=onec_data["Дата"],
        quantity=onec_data["Количество"],
        price=onec_data["Цена"],
        revenue=onec_data["Сумма"]
    )
