from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.forecasting.models.kaggle_entities import Category, Item, Shop
from src.features.inventory.models.warehouse import Warehouse
from src.features.products.models.product_model import Product
from src.features.sales.models.sale_model import Sale

from ..repositories.sync_state_repository import SyncStateRepository
from ..schemas.sync_schema import IncrementalImportRequest

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    received: int = 0
    inserted_sales: int = 0
    skipped_invalid: int = 0
    errors: list[str] | None = None
    last_sync_at: datetime | None = None


def _normalize_str(value: str | None) -> str | None:
    if value is None:
        return None
    v = value.strip()
    return v or None


def _parse_sale_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise ValueError("invalid date")


async def import_incremental_sales(
    session: AsyncSession,
    payload: IncrementalImportRequest,
) -> dict:
    result = ImportResult(received=len(payload.sales), errors=[])
    valid_rows: list[dict] = []
    max_sale_date: date | None = None

    for idx, row in enumerate(payload.sales):
        try:
            item_external_id = _normalize_str(row.item_id)
            shop_external_id = _normalize_str(row.shop_id)
            if not item_external_id or not shop_external_id:
                result.skipped_invalid += 1
                logger.warning("Skipping row %s due to missing item_id/shop_id", idx)
                continue

            sale_date = _parse_sale_date(row.date)
            if max_sale_date is None or sale_date > max_sale_date:
                max_sale_date = sale_date

            valid_rows.append(
                {
                    "sale_date": sale_date,
                    "shop_external_id": shop_external_id,
                    "shop_name": _normalize_str(row.shop_name) or f"Shop {shop_external_id[:8]}",
                    "item_external_id": item_external_id,
                    "item_name": _normalize_str(row.item_name) or f"Item {item_external_id[:8]}",
                    "category_external_id": _normalize_str(row.item_category_id),
                    "category_name": _normalize_str(row.item_category_name),
                    "price": float(row.item_price or 0.0),
                    "quantity": float(row.item_cnt_day or 0.0),
                    "date_block_num": row.date_block_num,
                }
            )
        except Exception as exc:  # noqa: BLE001
            result.skipped_invalid += 1
            err = f"row {idx}: {exc}"
            result.errors.append(err)
            logger.exception("Failed to normalize incremental row %s", idx)

    if not valid_rows:
        fallback_sync = datetime.now(timezone.utc)
        async with session.begin():
            await SyncStateRepository(session).update_last_sync("sales", fallback_sync)
        result.last_sync_at = fallback_sync
        return result.__dict__

    categories_payload = [
        {"external_id": r["category_external_id"], "category_name": r["category_name"] or "Unknown"}
        for r in valid_rows
        if r["category_external_id"] is not None
    ]
    categories_payload = list({x["external_id"]: x for x in categories_payload}.values())

    items_payload = [
        {"external_id": r["item_external_id"], "item_name": r["item_name"], "category_external_id": r["category_external_id"]}
        for r in valid_rows
    ]
    items_payload = list({x["external_id"]: x for x in items_payload}.values())

    shops_payload = [
        {"external_id": r["shop_external_id"], "shop_name": r["shop_name"]}
        for r in valid_rows
    ]
    shops_payload = list({x["external_id"]: x for x in shops_payload}.values())

    async with session.begin():
        if categories_payload:
            category_stmt = insert(Category).values(
                [{"external_id": c["external_id"], "category_name": c["category_name"]} for c in categories_payload]
            )
            category_stmt = category_stmt.on_conflict_do_update(
                index_elements=[Category.external_id],
                set_={"category_name": category_stmt.excluded.category_name},
            )
            await session.execute(category_stmt)

        shop_stmt = insert(Shop).values(shops_payload)
        shop_stmt = shop_stmt.on_conflict_do_update(
            index_elements=[Shop.external_id],
            set_={"shop_name": shop_stmt.excluded.shop_name},
        )
        await session.execute(shop_stmt)

        category_rows = await session.execute(select(Category.category_id, Category.external_id))
        category_id_by_external = {ext: cid for cid, ext in category_rows.all() if ext}

        item_values = [
            {
                "external_id": i["external_id"],
                "item_name": i["item_name"],
                "category_id": category_id_by_external.get(i["category_external_id"]),
            }
            for i in items_payload
        ]
        item_stmt = insert(Item).values(item_values)
        item_stmt = item_stmt.on_conflict_do_update(
            index_elements=[Item.external_id],
            set_={
                "item_name": item_stmt.excluded.item_name,
                "category_id": item_stmt.excluded.category_id,
            },
        )
        await session.execute(item_stmt)

        item_rows = await session.execute(select(Item.item_id, Item.external_id))
        item_id_by_external = {ext: iid for iid, ext in item_rows.all() if ext}
        shop_rows = await session.execute(select(Shop.shop_id, Shop.external_id))
        shop_id_by_external = {ext: sid for sid, ext in shop_rows.all() if ext}

        product_values = [
            {
                "external_id": i["external_id"],
                "name": i["item_name"],
                "category": (next((r["category_name"] for r in valid_rows if r["item_external_id"] == i["external_id"]), None) or ""),
                "item_id": item_id_by_external.get(i["external_id"]),
            }
            for i in items_payload
        ]
        product_stmt = insert(Product).values(product_values)
        product_stmt = product_stmt.on_conflict_do_update(
            index_elements=[Product.external_id],
            set_={
                "name": product_stmt.excluded.name,
                "category": product_stmt.excluded.category,
                "item_id": product_stmt.excluded.item_id,
            },
        )
        await session.execute(product_stmt)

        warehouse_values = [
            {
                "external_id": s["external_id"],
                "name": s["shop_name"],
                "shop_id": shop_id_by_external.get(s["external_id"]),
            }
            for s in shops_payload
        ]
        warehouse_stmt = insert(Warehouse).values(warehouse_values)
        warehouse_stmt = warehouse_stmt.on_conflict_do_update(
            index_elements=[Warehouse.external_id],
            set_={
                "name": warehouse_stmt.excluded.name,
                "shop_id": warehouse_stmt.excluded.shop_id,
            },
        )
        await session.execute(warehouse_stmt)

        product_rows = await session.execute(select(Product.id, Product.external_id))
        product_id_by_external = {ext: pid for pid, ext in product_rows.all() if ext}
        warehouse_rows = await session.execute(select(Warehouse.id, Warehouse.external_id))
        warehouse_id_by_external = {ext: wid for wid, ext in warehouse_rows.all() if ext}

        sale_values = []
        for r in valid_rows:
            product_id = product_id_by_external.get(r["item_external_id"])
            warehouse_id = warehouse_id_by_external.get(r["shop_external_id"])
            if not product_id or not warehouse_id:
                result.skipped_invalid += 1
                continue
            sale_values.append(
                {
                    "sale_date": r["sale_date"],
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "quantity": r["quantity"],
                    "price": r["price"],
                    "import_extras": {
                        "source": "1c_incremental",
                        "date_block_num": r["date_block_num"],
                    },
                }
            )

        if sale_values:
            sales_stmt = insert(Sale).values(sale_values)
            sales_stmt = sales_stmt.on_conflict_do_nothing(
                index_elements=[Sale.sale_date, Sale.warehouse_id, Sale.product_id]
            )
            sales_result = await session.execute(sales_stmt)
            result.inserted_sales = sales_result.rowcount or 0

        sync_at = datetime.combine(max_sale_date or date.today(), datetime.min.time(), tzinfo=timezone.utc)
        await SyncStateRepository(session).update_last_sync("sales", sync_at)
        result.last_sync_at = sync_at

    return result.__dict__
