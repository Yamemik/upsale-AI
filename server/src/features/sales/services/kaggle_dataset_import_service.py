from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Literal

from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.forecasting.models.kaggle_entities import Category, Item, Shop
from src.features.inventory.models.inventory import Inventory
from src.features.inventory.models.warehouse import Warehouse
from src.features.products.models.product_model import Product
from src.features.sales.models.sale_model import Sale
from src.features.sales.schemas.kaggle_import_schema import (
    KaggleImportRunResult,
    KaggleImportStepResult,
)

STEP_ORDER = [
    "categories",
    "items_ml",
    "products",
    "warehouses",
    "sales",
    "inventory",
]

STEP_TITLE: dict[str, str] = {
    "categories": "categories <- item_categories.csv",
    "items_ml": "items (ML слой) <- items.csv",
    "products": "products (бизнес слой) <- items.csv",
    "warehouses": "warehouses <- shops.csv",
    "sales": "sales (история) <- sales_train.csv",
    "inventory": "inventory (остатки) <- inventory.csv/расчет",
}


def _parse_float(raw: object) -> float:
    s = str(raw).strip().replace(" ", "").replace(",", ".")
    return float(s) if s else 0.0


def _parse_date(raw: object) -> date:
    s = str(raw).strip()
    if not s:
        raise ValueError("empty date")
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            chunk = s[:10] if fmt != "%Y-%m-%d %H:%M:%S" else s[:19]
            return datetime.strptime(chunk, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"unrecognized date: {s!r}")


def _read_csv_rows(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        clean = {str(k).strip(): (str(v).strip() if v is not None else "") for k, v in row.items() if k}
        if any(clean.values()):
            rows.append(clean)
    return rows


class KaggleDatasetImportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run(
        self,
        *,
        mode: Literal["upsert", "reload"],
        dry_run: bool,
        steps_requested: list[str],
        categories_bytes: bytes | None,
        items_bytes: bytes | None,
        shops_bytes: bytes | None,
        sales_bytes: bytes | None,
        inventory_bytes: bytes | None,
    ) -> KaggleImportRunResult:
        steps: list[KaggleImportStepResult] = []

        if mode == "reload":
            try:
                await self._reload_cleanup_for_requested_steps(steps_requested, dry_run=dry_run)
            except Exception:
                await self.db.rollback()
                raise

        categories_rows = _read_csv_rows(categories_bytes) if categories_bytes else []
        items_rows = _read_csv_rows(items_bytes) if items_bytes else []
        shops_rows = _read_csv_rows(shops_bytes) if shops_bytes else []
        sales_rows = _read_csv_rows(sales_bytes) if sales_bytes else []
        inventory_rows = _read_csv_rows(inventory_bytes) if inventory_bytes else []

        for step in STEP_ORDER:
            if step not in steps_requested:
                continue
            try:
                if step == "categories":
                    steps.append(await self._import_categories(categories_rows, dry_run=dry_run))
                elif step == "items_ml":
                    steps.append(await self._import_items_ml(items_rows, dry_run=dry_run))
                elif step == "products":
                    steps.append(await self._import_products(items_rows, dry_run=dry_run))
                elif step == "warehouses":
                    steps.append(await self._import_warehouses(shops_rows, dry_run=dry_run))
                elif step == "sales":
                    steps.append(await self._import_sales(sales_rows, dry_run=dry_run))
                elif step == "inventory":
                    steps.append(
                        await self._import_inventory(
                            inventory_rows,
                            dry_run=dry_run,
                            allow_calculated_fallback=not bool(inventory_rows),
                        )
                    )
            except Exception as e:
                await self.db.rollback()
                raise RuntimeError(f"ошибка шага '{step}': {e}") from e

        if dry_run:
            await self.db.rollback()
        else:
            await self.db.commit()

        totals = {
            "rows_read": sum(s.rows_read for s in steps),
            "inserted": sum(s.inserted for s in steps),
            "updated": sum(s.updated for s in steps),
            "skipped": sum(s.skipped for s in steps),
            "errors": sum(len(s.errors) for s in steps),
        }
        return KaggleImportRunResult(
            mode=mode,
            dry_run=dry_run,
            steps_requested=steps_requested,
            steps_executed=steps,
            totals=totals,
        )

    async def _reload_cleanup_for_requested_steps(self, steps_requested: list[str], *, dry_run: bool) -> None:
        # Безопасная очистка с учетом FK:
        # inventory/sales -> warehouses/products -> items -> categories.
        # Для верхнеуровневых справочников очищаем зависимые данные заранее,
        # иначе Postgres может выбросить FK violation и дать 500.
        needs_parent_cleanup = any(
            s in steps_requested for s in ("warehouses", "products", "items_ml", "categories")
        )
        if "inventory" in steps_requested or needs_parent_cleanup:
            await self.db.execute(delete(Inventory))
        if "sales" in steps_requested or needs_parent_cleanup:
            await self.db.execute(delete(Sale))
        if "warehouses" in steps_requested:
            await self.db.execute(delete(Warehouse))
            await self.db.execute(delete(Shop))
        if "products" in steps_requested:
            await self.db.execute(delete(Product))
        if "items_ml" in steps_requested:
            await self.db.execute(delete(Item))
        if "categories" in steps_requested:
            await self.db.execute(delete(Category))
        if dry_run:
            await self.db.flush()

    async def _import_categories(self, rows: list[dict[str, str]], *, dry_run: bool) -> KaggleImportStepResult:
        out = KaggleImportStepResult(step="categories", title=STEP_TITLE["categories"], rows_read=len(rows))
        for i, row in enumerate(rows, start=1):
            try:
                cid = int(row.get("item_category_id", ""))
                cname = row.get("item_category_name", "").strip()
                if not cname:
                    raise ValueError("empty item_category_name")
                existing = await self.db.get(Category, cid)
                if existing:
                    if existing.category_name != cname:
                        existing.category_name = cname
                        out.updated += 1
                    else:
                        out.skipped += 1
                else:
                    self.db.add(Category(category_id=cid, category_name=cname))
                    out.inserted += 1
            except (ValueError, TypeError, KeyError) as e:
                out.skipped += 1
                out.errors.append(f"row {i}: {e}")
        if dry_run:
            await self.db.flush()
        return out

    async def _import_items_ml(self, rows: list[dict[str, str]], *, dry_run: bool) -> KaggleImportStepResult:
        out = KaggleImportStepResult(step="items_ml", title=STEP_TITLE["items_ml"], rows_read=len(rows))
        for i, row in enumerate(rows, start=1):
            try:
                item_id = int(row.get("item_id", ""))
                item_name = row.get("item_name", "").strip()
                category_id = int(row.get("item_category_id", ""))
                if not item_name:
                    raise ValueError("empty item_name")
                existing = await self.db.get(Item, item_id)
                if existing:
                    changed = False
                    if existing.item_name != item_name:
                        existing.item_name = item_name
                        changed = True
                    if existing.category_id != category_id:
                        existing.category_id = category_id
                        changed = True
                    out.updated += 1 if changed else 0
                    out.skipped += 0 if changed else 1
                else:
                    self.db.add(Item(item_id=item_id, item_name=item_name, category_id=category_id))
                    out.inserted += 1
            except (ValueError, TypeError, KeyError) as e:
                out.skipped += 1
                out.errors.append(f"row {i}: {e}")
        if dry_run:
            await self.db.flush()
        return out

    async def _import_products(self, rows: list[dict[str, str]], *, dry_run: bool) -> KaggleImportStepResult:
        out = KaggleImportStepResult(step="products", title=STEP_TITLE["products"], rows_read=len(rows))
        category_names = {
            c.category_id: c.category_name
            for c in (await self.db.execute(select(Category))).scalars().all()
        }
        for i, row in enumerate(rows, start=1):
            try:
                item_id = int(row.get("item_id", ""))
                item_name = row.get("item_name", "").strip()
                category_id = int(row.get("item_category_id", ""))
                if not item_name:
                    raise ValueError("empty item_name")
                ext = f"kaggle_item_{item_id}"
                category = category_names.get(category_id, f"category_{category_id}")
                stmt = select(Product.id, Product.name, Product.category).where(Product.external_id == ext)
                existing = (await self.db.execute(stmt)).first()
                if existing:
                    pid, old_name, old_category = existing
                    changed = False
                    values: dict[str, object] = {}
                    if old_name != item_name:
                        values["name"] = item_name
                        changed = True
                    if old_category != category:
                        values["category"] = category
                        changed = True
                    if changed:
                        await self.db.execute(
                            update(Product).where(Product.id == pid).values(**values)
                        )
                    out.updated += 1 if changed else 0
                    out.skipped += 0 if changed else 1
                else:
                    await self.db.execute(
                        insert(Product).values(
                            external_id=ext,
                            name=item_name,
                            category=category,
                        )
                    )
                    out.inserted += 1
            except (ValueError, TypeError, KeyError) as e:
                out.skipped += 1
                out.errors.append(f"row {i}: {e}")
        if dry_run:
            await self.db.flush()
        return out

    async def _import_warehouses(self, rows: list[dict[str, str]], *, dry_run: bool) -> KaggleImportStepResult:
        out = KaggleImportStepResult(step="warehouses", title=STEP_TITLE["warehouses"], rows_read=len(rows))
        for i, row in enumerate(rows, start=1):
            try:
                shop_id = int(row.get("shop_id", ""))
                shop_name = row.get("shop_name", "").strip() or f"Shop {shop_id}"
                existing_shop = await self.db.get(Shop, shop_id)
                if existing_shop:
                    if existing_shop.shop_name != shop_name:
                        existing_shop.shop_name = shop_name
                        out.updated += 1
                    else:
                        out.skipped += 1
                else:
                    self.db.add(Shop(shop_id=shop_id, shop_name=shop_name))
                    out.inserted += 1

                ext = f"kaggle_shop_{shop_id}"
                stmt = select(Warehouse).where(Warehouse.external_id == ext)
                wh = (await self.db.execute(stmt)).scalar_one_or_none()
                if wh:
                    wh_changed = False
                    if wh.name != shop_name:
                        wh.name = shop_name
                        wh_changed = True
                    if wh.shop_id != shop_id:
                        wh.shop_id = shop_id
                        wh_changed = True
                    out.updated += 1 if wh_changed else 0
                    out.skipped += 0 if wh_changed else 1
                else:
                    self.db.add(
                        Warehouse(
                            external_id=ext,
                            name=shop_name,
                            shop_id=shop_id,
                        )
                    )
                    out.inserted += 1
            except (ValueError, TypeError, KeyError) as e:
                out.skipped += 1
                out.errors.append(f"row {i}: {e}")
        if dry_run:
            await self.db.flush()
        return out

    async def _import_sales(self, rows: list[dict[str, str]], *, dry_run: bool) -> KaggleImportStepResult:
        out = KaggleImportStepResult(step="sales", title=STEP_TITLE["sales"], rows_read=len(rows))
        warehouse_by_shop: dict[int, int] = {}
        for wid, shop_id in (
            await self.db.execute(select(Warehouse.id, Warehouse.shop_id).where(Warehouse.shop_id.is_not(None)))
        ).all():
            if shop_id is not None:
                warehouse_by_shop[int(shop_id)] = int(wid)

        for i, row in enumerate(rows, start=1):
            try:
                item_id = int(row.get("item_id", ""))
                shop_id = int(row.get("shop_id", ""))
                sale_date = _parse_date(row.get("date", ""))
                price = _parse_float(row.get("item_price", "0"))
                quantity = _parse_float(row.get("item_cnt_day", "0"))

                product_ext = f"kaggle_item_{item_id}"
                product_id = (
                    await self.db.execute(select(Product.id).where(Product.external_id == product_ext))
                ).scalar_one_or_none()
                warehouse_id = warehouse_by_shop.get(shop_id)
                if product_id is None or warehouse_id is None:
                    raise ValueError(f"missing product/warehouse for item_id={item_id}, shop_id={shop_id}")

                exists_stmt = select(Sale.id).where(
                    and_(
                        Sale.product_id == product_id,
                        Sale.warehouse_id == warehouse_id,
                        Sale.sale_date == sale_date,
                        Sale.quantity == quantity,
                        Sale.price == price,
                    )
                )
                exists = (await self.db.execute(exists_stmt)).scalar_one_or_none()
                if exists is not None:
                    out.skipped += 1
                    continue

                self.db.add(
                    Sale(
                        product_id=int(product_id),
                        warehouse_id=int(warehouse_id),
                        sale_date=sale_date,
                        quantity=quantity,
                        price=price,
                        revenue=quantity * price,
                        import_extras={
                            "source": "kaggle_sales_train",
                            "item_id": item_id,
                            "shop_id": shop_id,
                            "date_block_num": row.get("date_block_num", ""),
                        },
                    )
                )
                out.inserted += 1
            except (ValueError, TypeError, KeyError) as e:
                out.skipped += 1
                out.errors.append(f"row {i}: {e}")
        if dry_run:
            await self.db.flush()
        return out

    async def _import_inventory(
        self,
        rows: list[dict[str, str]],
        *,
        dry_run: bool,
        allow_calculated_fallback: bool,
    ) -> KaggleImportStepResult:
        out = KaggleImportStepResult(step="inventory", title=STEP_TITLE["inventory"], rows_read=len(rows))

        if rows:
            await self._import_inventory_rows(rows, out)
        elif allow_calculated_fallback:
            await self._rebuild_inventory_from_sales(out)

        if dry_run:
            await self.db.flush()
        return out

    async def _import_inventory_rows(self, rows: list[dict[str, str]], out: KaggleImportStepResult) -> None:
        warehouse_by_shop: dict[int, int] = {}
        for wid, shop_id in (
            await self.db.execute(select(Warehouse.id, Warehouse.shop_id).where(Warehouse.shop_id.is_not(None)))
        ).all():
            if shop_id is not None:
                warehouse_by_shop[int(shop_id)] = int(wid)
        for i, row in enumerate(rows, start=1):
            try:
                item_id = int(row.get("item_id", ""))
                shop_id = int(row.get("shop_id", ""))
                stock_raw = row.get("stock_quantity") or row.get("stock") or row.get("quantity") or "0"
                stock = _parse_float(stock_raw)
                product_ext = f"kaggle_item_{item_id}"
                product_id = (
                    await self.db.execute(select(Product.id).where(Product.external_id == product_ext))
                ).scalar_one_or_none()
                warehouse_id = warehouse_by_shop.get(shop_id)
                if product_id is None or warehouse_id is None:
                    raise ValueError(f"missing product/warehouse for item_id={item_id}, shop_id={shop_id}")
                stmt = select(Inventory).where(
                    and_(
                        Inventory.product_id == int(product_id),
                        Inventory.warehouse_id == int(warehouse_id),
                    )
                )
                existing = (await self.db.execute(stmt)).scalar_one_or_none()
                if existing:
                    if existing.stock_quantity != stock:
                        existing.stock_quantity = stock
                        out.updated += 1
                    else:
                        out.skipped += 1
                else:
                    self.db.add(
                        Inventory(
                            product_id=int(product_id),
                            warehouse_id=int(warehouse_id),
                            stock_quantity=stock,
                        )
                    )
                    out.inserted += 1
            except (ValueError, TypeError, KeyError) as e:
                out.skipped += 1
                out.errors.append(f"row {i}: {e}")

    async def _rebuild_inventory_from_sales(self, out: KaggleImportStepResult) -> None:
        sales = (await self.db.execute(select(Sale))).scalars().all()
        acc: dict[tuple[int, int], float] = {}
        for s in sales:
            if s.product_id is None or s.warehouse_id is None:
                continue
            key = (int(s.product_id), int(s.warehouse_id))
            acc[key] = acc.get(key, 0.0) + float(s.quantity or 0.0)

        out.rows_read = len(acc)
        for (product_id, warehouse_id), qty in acc.items():
            # Для демо-снимка не храним отрицательные остатки.
            stock = max(0.0, qty)
            stmt = select(Inventory).where(
                and_(
                    Inventory.product_id == product_id,
                    Inventory.warehouse_id == warehouse_id,
                )
            )
            existing = (await self.db.execute(stmt)).scalar_one_or_none()
            if existing:
                if existing.stock_quantity != stock:
                    existing.stock_quantity = stock
                    out.updated += 1
                else:
                    out.skipped += 1
            else:
                self.db.add(
                    Inventory(
                        product_id=product_id,
                        warehouse_id=warehouse_id,
                        stock_quantity=stock,
                    )
                )
                out.inserted += 1

