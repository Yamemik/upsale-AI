"""
Загрузка строк продаж из 1С OData и приведение к полям для Kaggle-выгрузки / импорта в БД.
Имена полей в OData зависят от конфигурации — при расхождениях правьте маппинг ниже.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from src.config.settings import Settings

from ..client.odata_client import ODataClient


def _pick(d: dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def _lines_from_doc(doc: dict[str, Any], expand_key: str) -> list[dict[str, Any]]:
    raw = doc.get(expand_key)
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return [raw]
    return []


def flatten_realisation_documents(
    documents: list[dict[str, Any]],
    expand_key: str,
) -> list[dict[str, Any]]:
    """Одна строка результата на строку табличной части документа."""
    out: list[dict[str, Any]] = []
    for doc in documents:
        doc_date = _pick(doc, "Date", "Дата")
        doc_shop = _pick(doc, "Склад_Key", "Склад", "Магазин_Key")
        for line in _lines_from_doc(doc, expand_key):
            shop_key = _pick(line, "Склад_Key", "Склад") or doc_shop
            item_key = _pick(line, "Номенклатура_Key", "Номенклатура")
            qty = _pick(line, "Количество", "Quantity")
            price = _pick(line, "Цена", "Price")
            out.append(
                {
                    "sale_date": doc_date,
                    "shop_key": str(shop_key) if shop_key is not None else "",
                    "item_key": str(item_key) if item_key is not None else "",
                    "item_price": float(price) if price is not None else 0.0,
                    "item_cnt_day": float(qty) if qty is not None else 0.0,
                    "shop_name": None,
                    "item_name": _pick(line, "Номенклатура", "Номенклатура_Type"),
                    "category_key": None,
                    "category_name": None,
                }
            )
    return out


async def _ref_description_map(
    client: ODataClient,
    catalog_path: str,
) -> dict[str, str]:
    try:
        rows = await client.fetch_all_pages(
            catalog_path,
            {"$format": "json", "$select": "Ref_Key,Description"},
        )
    except Exception:
        return {}
    result: dict[str, str] = {}
    for r in rows:
        ref = r.get("Ref_Key")
        if ref:
            result[str(ref)] = str(r.get("Description") or "")
    return result


async def _nomenclature_parent_map(
    client: ODataClient,
    catalog_path: str,
) -> dict[str, str]:
    """Ref_Key номенклатуры -> Parent_Key (группа категории)."""
    rows: list[dict[str, Any]] = []
    for select in (
        "Ref_Key,Parent_Key,ЭтоГруппа",
        "Ref_Key,Parent_Key,ThisIsGroup",
        "Ref_Key,Parent_Key",
    ):
        try:
            rows = await client.fetch_all_pages(
                catalog_path,
                {"$format": "json", "$select": select},
            )
            break
        except Exception:
            continue
    if not rows:
        return {}
    result: dict[str, str] = {}
    for r in rows:
        ref = r.get("Ref_Key")
        if not ref:
            continue
        is_group = r.get("ЭтоГруппа")
        if is_group is None:
            is_group = r.get("ThisIsGroup")
        if is_group is True:
            continue
        pk = r.get("Parent_Key")
        if pk:
            result[str(ref)] = str(pk)
    return result


async def fetch_kaggle_source_rows(
    client: ODataClient,
    settings: Settings,
    *,
    date_from: date | None = None,
) -> list[dict[str, Any]]:
    """Строки для build_kaggle_dataframes / импорта в БД (после обогащения справочниками)."""
    params: dict[str, str] = {
        "$format": "json",
        "$expand": settings.INTEGRATION_1C_ODATA_EXPAND_LINE_ITEMS,
    }
    if date_from is not None:
        field = settings.INTEGRATION_1C_ODATA_DOCUMENT_DATE_FIELD
        # Типичный фильтр OData для 1С
        dt = f"datetime'{date_from.isoformat()}T00:00:00'"
        params["$filter"] = f"{field} ge {dt}"

    docs = await client.fetch_all_pages(
        settings.INTEGRATION_1C_ODATA_DOCUMENT_PATH,
        params,
    )
    flat = flatten_realisation_documents(
        docs,
        settings.INTEGRATION_1C_ODATA_EXPAND_LINE_ITEMS,
    )

    shop_names = await _ref_description_map(
        client, settings.INTEGRATION_1C_ODATA_SHOP_CATALOG
    )
    item_names = await _ref_description_map(
        client, settings.INTEGRATION_1C_ODATA_ITEM_CATALOG
    )
    parent_by_item = await _nomenclature_parent_map(
        client, settings.INTEGRATION_1C_ODATA_ITEM_CATALOG
    )
    group_names = await _ref_description_map(
        client, settings.INTEGRATION_1C_ODATA_ITEM_CATALOG
    )

    for row in flat:
        sk = row["shop_key"]
        if sk and sk in shop_names:
            row["shop_name"] = shop_names[sk]
        ik = row["item_key"]
        if ik and ik in item_names:
            row["item_name"] = item_names.get(ik) or row.get("item_name")
        if ik and ik in parent_by_item:
            pk = parent_by_item[ik]
            row["category_key"] = pk
            row["category_name"] = group_names.get(pk)

    return flat
