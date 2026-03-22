"""
Импорт строк продаж из 1С OData в таблицу sales (дополнение истории после первичного CSV).
Внешние ключи: onec_nom:{guid}, onec_wh:{guid}.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings
from src.features.inventory.repositories.warehouse_repository import WarehouseRepository
from src.features.products.repositories.product_repository import ProductRepository
from src.features.sales.models.sale_model import Sale
from src.features.sales.repositories.sale_repository import SalesRepository

from ..client.odata_client import ODataClient
from .kaggle_export_service import _to_date
from .onec_kaggle_fetch_service import fetch_kaggle_source_rows

_BATCH = 500
_MAX_RETURN_ERRORS = 50


async def resolve_sync_date_from(
    session: AsyncSession,
    settings: Settings,
    *,
    lookback_days_override: int | None = None,
) -> date:
    if lookback_days_override is not None:
        return date.today() - timedelta(days=max(0, lookback_days_override))
    if settings.INTEGRATION_1C_SYNC_FROM_MAX_SALE_DATE:
        repo = SalesRepository(session)
        max_d = await repo.max_sale_date()
        if max_d is not None:
            return max_d - timedelta(days=settings.INTEGRATION_1C_SYNC_OVERLAP_DAYS)
    return date.today() - timedelta(days=settings.INTEGRATION_1C_SYNC_LOOKBACK_DAYS)


async def import_onec_sales_from_odata(
    session: AsyncSession,
    settings: Settings,
    *,
    date_from: date | None = None,
    lookback_days_override: int | None = None,
) -> dict[str, Any]:
    if not settings.INTEGRATION_1C_BASE_URL or not settings.INTEGRATION_1C_USERNAME:
        return {
            "imported": 0,
            "errors": ["Интеграция 1С не настроена (INTEGRATION_1C_BASE_URL / USERNAME)"],
            "date_from": None,
        }

    if date_from is None:
        date_from = await resolve_sync_date_from(
            session,
            settings,
            lookback_days_override=lookback_days_override,
        )

    client = ODataClient(
        base_url=settings.INTEGRATION_1C_BASE_URL,
        username=settings.INTEGRATION_1C_USERNAME,
        password=settings.INTEGRATION_1C_PASSWORD or "",
    )

    rows = await fetch_kaggle_source_rows(
        client,
        settings,
        date_from=date_from,
    )

    products = ProductRepository(session)
    warehouses = WarehouseRepository(session)
    sales_repo = SalesRepository(session)

    out_sales: list[Sale] = []
    errors: list[str] = []
    imported = 0

    for i, row in enumerate(rows):
        sd = _to_date(row.get("sale_date"))
        if sd is None:
            if len(errors) < _MAX_RETURN_ERRORS:
                errors.append(f"row {i}: bad sale_date")
            continue
        ik = str(row.get("item_key") or "").strip()
        sk = str(row.get("shop_key") or "").strip()
        if not ik or not sk:
            if len(errors) < _MAX_RETURN_ERRORS:
                errors.append(f"row {i}: missing item_key or shop_key")
            continue

        pext = f"onec_nom:{ik}"
        wext = f"onec_wh:{sk}"
        iname = (row.get("item_name") or "").strip() or f"Номенклатура {ik[:16]}"
        sname = (row.get("shop_name") or "").strip() or f"Склад {sk[:16]}"

        product = await products.get_or_create_by_external_id(
            pext,
            iname,
            category="",
        )
        warehouse = await warehouses.get_or_create_by_external_id(
            wext,
            sname,
        )

        qty = float(row.get("item_cnt_day") or 0.0)
        price = float(row.get("item_price") or 0.0)
        revenue = qty * price

        extras: dict[str, Any] = {"source": "1c"}
        if row.get("category_key"):
            extras["category_key"] = row["category_key"]
        if row.get("category_name"):
            extras["category_name"] = row["category_name"]

        out_sales.append(
            Sale(
                product_id=product.id,
                warehouse_id=warehouse.id,
                sale_date=sd,
                quantity=qty,
                price=price,
                revenue=revenue,
                import_extras=extras,
            )
        )
        imported += 1

        if len(out_sales) >= _BATCH:
            await sales_repo.add_all(out_sales)
            out_sales.clear()

    if out_sales:
        await sales_repo.add_all(out_sales)

    return {
        "imported": imported,
        "errors": errors,
        "date_from": date_from.isoformat(),
        "rows_fetched": len(rows),
    }
