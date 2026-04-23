"""add sync_state and incremental import indexes

Revision ID: 9f3c1a2b7d11
Revises: 7b1d4f8c2a10
Create Date: 2026-04-20
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f3c1a2b7d11"
down_revision: Union[str, Sequence[str], None] = "7b1d4f8c2a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(table_name: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return table_name in insp.get_table_names()


def _has_column(table_name: str, column_name: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return any(c["name"] == column_name for c in insp.get_columns(table_name))


def _has_index(table_name: str, index_name: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return any(i["name"] == index_name for i in insp.get_indexes(table_name))


def _is_nullable(table_name: str, column_name: str) -> bool:
    insp = sa.inspect(op.get_bind())
    for col in insp.get_columns(table_name):
        if col["name"] == column_name:
            return bool(col.get("nullable", False))
    return False


def upgrade() -> None:
    if not _has_table("sync_state"):
        op.create_table(
            "sync_state",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("entity", sa.String(length=64), nullable=False),
            sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_unique_constraint("uq_sync_state_entity", "sync_state", ["entity"])
        op.create_index("ix_sync_state_entity", "sync_state", ["entity"])

    if _has_table("categories") and not _has_column("categories", "external_id"):
        with op.batch_alter_table("categories") as batch_op:
            batch_op.add_column(sa.Column("external_id", sa.String(length=64), nullable=True))
        if not _has_index("categories", "ix_categories_external_id"):
            op.create_index("ix_categories_external_id", "categories", ["external_id"], unique=True)

    if _has_table("items") and not _has_column("items", "external_id"):
        with op.batch_alter_table("items") as batch_op:
            batch_op.add_column(sa.Column("external_id", sa.String(length=64), nullable=True))
        if not _has_index("items", "ix_items_external_id"):
            op.create_index("ix_items_external_id", "items", ["external_id"], unique=True)
    if _has_table("items") and not _is_nullable("items", "category_id"):
        with op.batch_alter_table("items") as batch_op:
            batch_op.alter_column("category_id", existing_type=sa.Integer(), nullable=True)

    if _has_table("shops") and not _has_column("shops", "external_id"):
        with op.batch_alter_table("shops") as batch_op:
            batch_op.add_column(sa.Column("external_id", sa.String(length=64), nullable=True))
        if not _has_index("shops", "ix_shops_external_id"):
            op.create_index("ix_shops_external_id", "shops", ["external_id"], unique=True)

    if _has_table("sales") and not _has_index("sales", "ux_sales_date_warehouse_product"):
        op.create_index(
            "ux_sales_date_warehouse_product",
            "sales",
            ["sale_date", "warehouse_id", "product_id"],
            unique=True,
        )


def downgrade() -> None:
    if _has_table("sales") and _has_index("sales", "ux_sales_date_warehouse_product"):
        op.drop_index("ux_sales_date_warehouse_product", table_name="sales")

    if _has_table("shops") and _has_index("shops", "ix_shops_external_id"):
        op.drop_index("ix_shops_external_id", table_name="shops")
    if _has_table("shops") and _has_column("shops", "external_id"):
        with op.batch_alter_table("shops") as batch_op:
            batch_op.drop_column("external_id")

    if _has_table("items") and _has_index("items", "ix_items_external_id"):
        op.drop_index("ix_items_external_id", table_name="items")
    if _has_table("items") and _is_nullable("items", "category_id"):
        with op.batch_alter_table("items") as batch_op:
            batch_op.alter_column("category_id", existing_type=sa.Integer(), nullable=False)
    if _has_table("items") and _has_column("items", "external_id"):
        with op.batch_alter_table("items") as batch_op:
            batch_op.drop_column("external_id")

    if _has_table("categories") and _has_index("categories", "ix_categories_external_id"):
        op.drop_index("ix_categories_external_id", table_name="categories")
    if _has_table("categories") and _has_column("categories", "external_id"):
        with op.batch_alter_table("categories") as batch_op:
            batch_op.drop_column("external_id")

    if _has_table("sync_state"):
        op.drop_index("ix_sync_state_entity", table_name="sync_state")
        op.drop_constraint("uq_sync_state_entity", "sync_state", type_="unique")
        op.drop_table("sync_state")
