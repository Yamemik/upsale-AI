from __future__ import annotations

import csv
import io
import logging
from datetime import date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.features.inventory.repositories.warehouse_repository import WarehouseRepository
from src.features.products.repositories.product_repository import ProductRepository
from src.features.sales.csv_import_mapping import row_dict_from_csv_row, split_core_and_extras
from src.features.sales.models.sale_model import Sale
from src.features.sales.repositories.sale_repository import SalesRepository

logger = logging.getLogger(__name__)

_MAX_ERROR_LINES = 50


def _parse_float(raw: object) -> float:
    s = str(raw).strip().replace(" ", "").replace(",", ".")
    return float(s)


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
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return date.fromisoformat(s[:10])
    raise ValueError(f"unrecognized date: {s!r}")


class SaleCsvImportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sales = SalesRepository(db)
        self.products = ProductRepository(db)
        self.warehouses = WarehouseRepository(db)

    async def import_csv_bytes(self, data: bytes) -> dict[str, object]:
        text = data.decode("utf-8-sig")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            return {"imported": 0, "skipped": 0, "errors": ["empty file"]}

        headers = [h.strip() for h in rows[0]]
        if not any(headers):
            return {"imported": 0, "skipped": 0, "errors": ["no header row"]}

        imported = 0
        skipped = 0
        errors: list[str] = []
        batch: list[Sale] = []
        batch_size = 500

        for i, values in enumerate(rows[1:], start=2):
            if len(errors) >= _MAX_ERROR_LINES:
                errors.append("… further errors omitted")
                break
            if not any(str(v).strip() for v in values):
                continue
            try:
                sale = await self._row_to_sale(headers, values)
            except (ValueError, TypeError, KeyError) as e:
                skipped += 1
                errors.append(f"row {i}: {e}")
                continue
            batch.append(sale)
            imported += 1
            if len(batch) >= batch_size:
                await self.sales.add_all(batch)
                batch.clear()

        if batch:
            await self.sales.add_all(batch)

        return {"imported": imported, "skipped": skipped, "errors": errors}

    async def _row_to_sale(self, headers: list[str], values: list[str]) -> Sale:
        padded = list(values) + [""] * max(0, len(headers) - len(values))
        logical_row = row_dict_from_csv_row(headers, padded[: len(headers)])
        core, extras = split_core_and_extras(logical_row)

        pid = core.get("product_id")
        pext = core.get("product_external_id")
        product_id: int | None = None
        if pid is not None and str(pid).strip() != "":
            product_id = int(str(pid).strip())
        elif pext is not None and str(pext).strip() != "":
            p = await self.products.get_by_external_id(str(pext).strip())
            if not p:
                raise ValueError(f"product external_id not found: {pext!r}")
            product_id = p.id
        else:
            raise ValueError("product_id or product_external_id required")

        wid = core.get("warehouse_id")
        wext = core.get("warehouse_external_id")
        warehouse_id: int | None = None
        if wid is not None and str(wid).strip() != "":
            warehouse_id = int(str(wid).strip())
        elif wext is not None and str(wext).strip() != "":
            w = await self.warehouses.get_by_external_id(str(wext).strip())
            if not w:
                raise ValueError(f"warehouse external_id not found: {wext!r}")
            warehouse_id = w.id
        else:
            raise ValueError("warehouse_id or warehouse_external_id required")

        for req in ("sale_date", "quantity", "price"):
            if req not in core or str(core[req]).strip() == "":
                raise ValueError(f"missing required field: {req}")

        sale_date = _parse_date(core["sale_date"])
        quantity = _parse_float(core["quantity"])
        price = _parse_float(core["price"])
        rev_raw = core.get("revenue")
        if rev_raw is None or str(rev_raw).strip() == "":
            revenue = quantity * price
        else:
            revenue = _parse_float(rev_raw)

        return Sale(
            product_id=product_id,
            warehouse_id=warehouse_id,
            sale_date=sale_date,
            quantity=quantity,
            price=price,
            revenue=revenue,
            import_extras=extras if extras else None,
        )


async def run_sales_csv_seed_if_configured(session: AsyncSession) -> None:
    path = settings.SALES_SEED_CSV_PATH
    if not path:
        return
    if settings.SALES_SEED_ONLY_IF_EMPTY:
        repo = SalesRepository(session)
        if await repo.count() > 0:
            return
    from pathlib import Path

    p = Path(path)
    if not p.is_file():
        logger.warning("SALES_SEED_CSV_PATH is set but file missing: %s", path)
        return
    data = p.read_bytes()
    result = await SaleCsvImportService(session).import_csv_bytes(data)
    logger.info(
        "Sales CSV seed from %s: imported=%s skipped=%s",
        path,
        result["imported"],
        result["skipped"],
    )
    if result.get("errors"):
        for err in result["errors"][:10]:
            logger.warning("Sales CSV seed: %s", err)
