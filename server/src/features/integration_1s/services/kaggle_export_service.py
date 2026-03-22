"""
Сборка CSV в формате Kaggle «Predict Future Sales»:
  sales_train.csv, shops.csv, items.csv, item_categories.csv

См. https://www.kaggle.com/c/competitive-data-science-predict-future-sales/data
"""

from __future__ import annotations

import io
import zipfile
from datetime import date, datetime
from typing import Any

import pandas as pd


# Порядок и имена колонок как в соревновании
SALES_TRAIN_COLUMNS = [
    "date",
    "date_block_num",
    "shop_id",
    "item_id",
    "item_price",
    "item_cnt_day",
]
SHOPS_COLUMNS = ["shop_name", "shop_id"]
ITEMS_COLUMNS = ["item_name", "item_id", "item_category_id"]
ITEM_CATEGORIES_COLUMNS = ["item_category_name", "item_category_id"]


def _to_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("/Date(") and s.endswith(")/"):
            try:
                ms = int(s[6:-2].split("-")[0])
                return datetime.fromtimestamp(ms / 1000.0).date()
            except (ValueError, IndexError):
                return None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(s[:19], fmt).date()
            except ValueError:
                continue
    return None


def _month_block_origin(dates: list[date]) -> tuple[int, int]:
    if not dates:
        return (2013, 1)
    m0 = min(dates)
    return (m0.year, m0.month)


def _date_block_num(d: date, origin: tuple[int, int]) -> int:
    y0, m0 = origin
    return (d.year - y0) * 12 + (d.month - m0)


def _stable_index(keys: list[str]) -> dict[str, int]:
    unique = sorted(set(keys))
    return {k: i for i, k in enumerate(unique)}


def build_kaggle_dataframes(
    rows: list[dict[str, Any]],
) -> dict[str, pd.DataFrame]:
    """
    rows: список словарей с полями:
      sale_date (date | str),
      shop_key (str) — внешний ключ склада/магазина,
      item_key (str) — внешний ключ номенклатуры,
      item_price (float),
      item_cnt_day (float),
      shop_name (str, optional),
      item_name (str, optional),
      category_key (str, optional) — ключ группы/категории в 1С,
      category_name (str, optional).
    """
    if not rows:
        return {
            "sales_train.csv": pd.DataFrame(columns=SALES_TRAIN_COLUMNS),
            "shops.csv": pd.DataFrame(columns=SHOPS_COLUMNS),
            "items.csv": pd.DataFrame(columns=ITEMS_COLUMNS),
            "item_categories.csv": pd.DataFrame(columns=ITEM_CATEGORIES_COLUMNS),
        }

    parsed: list[dict[str, Any]] = []
    for r in rows:
        sd = _to_date(r.get("sale_date"))
        if sd is None:
            continue
        parsed.append(
            {
                "sale_date": sd,
                "shop_key": str(r.get("shop_key") or ""),
                "item_key": str(r.get("item_key") or ""),
                "item_price": float(r.get("item_price") or 0.0),
                "item_cnt_day": float(r.get("item_cnt_day") or 0.0),
                "shop_name": r.get("shop_name"),
                "item_name": r.get("item_name"),
                "category_key": r.get("category_key"),
                "category_name": r.get("category_name"),
            }
        )

    if not parsed:
        return {
            "sales_train.csv": pd.DataFrame(columns=SALES_TRAIN_COLUMNS),
            "shops.csv": pd.DataFrame(columns=SHOPS_COLUMNS),
            "items.csv": pd.DataFrame(columns=ITEMS_COLUMNS),
            "item_categories.csv": pd.DataFrame(columns=ITEM_CATEGORIES_COLUMNS),
        }

    shop_map = _stable_index([p["shop_key"] for p in parsed if p["shop_key"]])
    item_map = _stable_index([p["item_key"] for p in parsed if p["item_key"]])

    cat_keys: list[str] = []
    for p in parsed:
        ck = p.get("category_key")
        if ck is not None and str(ck).strip():
            cat_keys.append(str(ck))
    cat_map = _stable_index(cat_keys)

    origin = _month_block_origin([p["sale_date"] for p in parsed])

    sales_rows: list[dict[str, Any]] = []
    for p in parsed:
        sid = shop_map.get(p["shop_key"], 0)
        iid = item_map.get(p["item_key"], 0)
        sales_rows.append(
            {
                "date": p["sale_date"].strftime("%d/%m/%Y"),
                "date_block_num": _date_block_num(p["sale_date"], origin),
                "shop_id": sid,
                "item_id": iid,
                "item_price": p["item_price"],
                "item_cnt_day": p["item_cnt_day"],
            }
        )

    shop_df_rows: list[dict[str, Any]] = []
    for sk, sid in sorted(shop_map.items(), key=lambda x: x[1]):
        name = next(
            (p["shop_name"] for p in parsed if p["shop_key"] == sk and p.get("shop_name")),
            None,
        )
        shop_df_rows.append(
            {
                "shop_name": name if name else f"shop_{sid}",
                "shop_id": sid,
            }
        )

    item_df_rows: list[dict[str, Any]] = []
    for ik, iid in sorted(item_map.items(), key=lambda x: x[1]):
        sample = next((p for p in parsed if p["item_key"] == ik), None)
        iname = (sample or {}).get("item_name") if sample else None
        ck = (sample or {}).get("category_key") if sample else None
        cid = cat_map.get(str(ck), 0) if ck is not None and str(ck).strip() else 0
        item_df_rows.append(
            {
                "item_name": iname if iname else f"item_{iid}",
                "item_id": iid,
                "item_category_id": cid,
            }
        )

    cat_df_rows: list[dict[str, Any]] = []
    for ck, cid in sorted(cat_map.items(), key=lambda x: x[1]):
        cname = next(
            (
                p["category_name"]
                for p in parsed
                if str(p.get("category_key")) == ck and p.get("category_name")
            ),
            None,
        )
        cat_df_rows.append(
            {
                "item_category_name": cname if cname else f"category_{cid}",
                "item_category_id": cid,
            }
        )

    needed_cat_ids = {r["item_category_id"] for r in item_df_rows}
    existing_cat_ids = {r["item_category_id"] for r in cat_df_rows}
    for nid in sorted(needed_cat_ids - existing_cat_ids):
        cat_df_rows.append(
            {"item_category_name": f"category_{nid}", "item_category_id": nid}
        )

    cat_df_rows.sort(key=lambda r: r["item_category_id"])

    return {
        "sales_train.csv": pd.DataFrame(sales_rows)[SALES_TRAIN_COLUMNS],
        "shops.csv": pd.DataFrame(shop_df_rows)[SHOPS_COLUMNS],
        "items.csv": pd.DataFrame(item_df_rows)[ITEMS_COLUMNS],
        "item_categories.csv": pd.DataFrame(cat_df_rows)[ITEM_CATEGORIES_COLUMNS],
    }


def kaggle_dataset_zip_bytes(dfs: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, df in dfs.items():
            zf.writestr(filename, df.to_csv(index=False))
    return buf.getvalue()
