"""
Маппинг заголовков CSV → логические поля строки продажи.

Формат датасета ВКР (пример):
  date,product_id,warehouse_id,sales,lag_1,lag_7,rolling_mean_7,price,stock_level,day_of_week,month

Здесь `sales` — объём продаж в штуках → quantity; `date` → sale_date;
lag_*, rolling_mean_*, stock_level, day_of_week, month попадают в import_extras
до появления отдельных колонок в модели.

Формат Kaggle «Predict Future Sales» (sales_train.csv): date, date_block_num,
shop_id, item_id, item_price, item_cnt_day — обрабатывается отдельной веткой
импорта (см. SaleCsvImportService), по умолчанию автоопределение по заголовкам.

Расширение: register_sale_csv_alias("заголовок", "логическое_поле") или правки
SALE_CSV_HEADER_ALIASES и обработки в SaleCsvImportService._row_to_sale.
"""

from __future__ import annotations

from typing import Any

SALE_CSV_HEADER_ALIASES: dict[str, str] = {
    # дата
    "date": "sale_date",
    "sale_date": "sale_date",
    "дата": "sale_date",
    # VKR / ML: объём в штуках
    "sales": "quantity",
    "qty": "quantity",
    "quantity": "quantity",
    "количество": "quantity",
    # product
    "product_id": "product_id",
    "productid": "product_id",
    "id_товара": "product_id",
    "товар_id": "product_id",
    "product_external_id": "product_external_id",
    "nomenclature_key": "product_external_id",
    "номенклатура_key": "product_external_id",
    "номенклатураkey": "product_external_id",
    "guid_товара": "product_external_id",
    "product_guid": "product_external_id",
    # warehouse
    "warehouse_id": "warehouse_id",
    "warehouseid": "warehouse_id",
    "id_склада": "warehouse_id",
    "склад_id": "warehouse_id",
    "warehouse_external_id": "warehouse_external_id",
    "warehouse_key": "warehouse_external_id",
    "склад_key": "warehouse_external_id",
    "складkey": "warehouse_external_id",
    # measures
    "price": "price",
    "цена": "price",
    "revenue": "revenue",
    "sum": "revenue",
    "amount": "revenue",
    "сумма": "revenue",
}

# Поля, которые участвуют в сборке Sale (остальное — в import_extras JSON)
SALE_ROW_CORE_FIELDS: frozenset[str] = frozenset(
    {
        "product_id",
        "product_external_id",
        "warehouse_id",
        "warehouse_external_id",
        "sale_date",
        "quantity",
        "price",
        "revenue",
    }
)


def register_sale_csv_alias(normalized_header: str, logical_field: str) -> None:
    SALE_CSV_HEADER_ALIASES[normalize_csv_header(normalized_header)] = logical_field


def normalize_csv_header(header: str) -> str:
    return header.replace("\ufeff", "").strip().lower().replace(" ", "_")


def is_kaggle_sales_train_headers(headers: list[str]) -> bool:
    """Колонки как в sales_train.csv (Kaggle Predict Future Sales)."""
    norm = {normalize_csv_header(h) for h in headers if h and str(h).strip()}
    required = {"date", "item_id", "shop_id", "item_price", "item_cnt_day"}
    return required.issubset(norm)


def logical_field_for_header(header: str) -> str:
    norm = normalize_csv_header(header)
    return SALE_CSV_HEADER_ALIASES.get(norm, norm)


def row_dict_from_csv_row(headers: list[str], values: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    seen_logical: set[str] = set()
    for h, raw in zip(headers, values):
        key_orig = h.replace("\ufeff", "").strip()
        if not key_orig:
            continue
        logical = logical_field_for_header(h)
        if logical not in seen_logical:
            seen_logical.add(logical)
            out[logical] = raw
        else:
            out[key_orig] = raw
    return out


def split_core_and_extras(logical_row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    core: dict[str, Any] = {}
    extras: dict[str, Any] = {}
    for k, v in logical_row.items():
        if k in SALE_ROW_CORE_FIELDS:
            core[k] = v
        else:
            if v is not None and str(v).strip() != "":
                extras[k] = v
    return core, extras
