"""upgrade schema for ml pipeline and 1c integration

Revision ID: 7b1d4f8c2a10
Revises: 3a7f2c9e1b00
Create Date: 2026-04-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b1d4f8c2a10"
down_revision: Union[str, Sequence[str], None] = "3a7f2c9e1b00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(c["name"] == column_name for c in insp.get_columns(table_name))


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(i["name"] == index_name for i in insp.get_indexes(table_name))


def _has_unique(table_name: str, unique_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(u["name"] == unique_name for u in insp.get_unique_constraints(table_name))


def _has_fk(table_name: str, fk_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return any(fk["name"] == fk_name for fk in insp.get_foreign_keys(table_name))


def _has_table(table_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return table_name in insp.get_table_names()


def upgrade() -> None:
    # products -> items bridge
    with op.batch_alter_table("products") as batch_op:
        if not _has_column("products", "item_id"):
            batch_op.add_column(sa.Column("item_id", sa.Integer(), nullable=True))
        if not _has_fk("products", "fk_products_item_id_items"):
            batch_op.create_foreign_key(
                "fk_products_item_id_items",
                "items",
                ["item_id"],
                ["item_id"],
                ondelete="SET NULL",
            )

    # warehouses -> shops bridge
    with op.batch_alter_table("warehouses") as batch_op:
        if not _has_column("warehouses", "shop_id"):
            batch_op.add_column(sa.Column("shop_id", sa.Integer(), nullable=True))
        if not _has_fk("warehouses", "fk_warehouses_shop_id_shops"):
            batch_op.create_foreign_key(
                "fk_warehouses_shop_id_shops",
                "shops",
                ["shop_id"],
                ["shop_id"],
                ondelete="SET NULL",
            )

    # features: new ML features + uniqueness
    with op.batch_alter_table("features") as batch_op:
        if not _has_column("features", "lag_6"):
            batch_op.add_column(sa.Column("lag_6", sa.Numeric(12, 3), nullable=True))
        if not _has_column("features", "rolling_mean_6"):
            batch_op.add_column(sa.Column("rolling_mean_6", sa.Numeric(12, 3), nullable=True))
        if not _has_column("features", "price_trend"):
            batch_op.add_column(sa.Column("price_trend", sa.Numeric(12, 6), nullable=True))
        if not _has_column("features", "month_num"):
            batch_op.add_column(sa.Column("month_num", sa.Integer(), nullable=True))
        if not _has_unique("features", "uq_features_shop_item_month"):
            batch_op.create_unique_constraint(
                "uq_features_shop_item_month",
                ["shop_id", "item_id", "month"],
            )

    # monthly_sales uniqueness
    with op.batch_alter_table("monthly_sales") as batch_op:
        if not _has_unique("monthly_sales", "uq_monthly_sales_shop_item_month"):
            batch_op.create_unique_constraint(
                "uq_monthly_sales_shop_item_month",
                ["shop_id", "item_id", "month"],
            )

    # forecasts cleanup + constraints
    with op.batch_alter_table("forecasts") as batch_op:
        if _has_column("forecasts", "predicted_cnt"):
            batch_op.drop_column("predicted_cnt")
        if _has_column("forecasts", "month"):
            batch_op.drop_column("month")

        if not _has_fk("forecasts", "fk_forecasts_shop_id_shops"):
            batch_op.create_foreign_key(
                "fk_forecasts_shop_id_shops",
                "shops",
                ["shop_id"],
                ["shop_id"],
            )
        if not _has_fk("forecasts", "fk_forecasts_item_id_items"):
            batch_op.create_foreign_key(
                "fk_forecasts_item_id_items",
                "items",
                ["item_id"],
                ["item_id"],
            )

        if not _has_unique("forecasts", "uq_forecasts_product_warehouse_target_model"):
            batch_op.create_unique_constraint(
                "uq_forecasts_product_warehouse_target_model",
                ["product_id", "warehouse_id", "target_date", "model_id"],
            )

    # inventory history
    if not _has_table("inventory_history"):
        op.create_table(
            "inventory_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
            sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouses.id"), nullable=False),
            sa.Column("stock_quantity", sa.Float(), nullable=False),
            sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    # sales revenue as generated value
    with op.batch_alter_table("sales") as batch_op:
        if _has_column("sales", "revenue"):
            batch_op.drop_column("revenue")
        batch_op.add_column(
            sa.Column(
                "revenue",
                sa.Float(),
                sa.Computed("quantity * price", persisted=True),
                nullable=True,
            )
        )

    # forecast explanations timestamp
    with op.batch_alter_table("forecast_explanations") as batch_op:
        if not _has_column("forecast_explanations", "created_at"):
            batch_op.add_column(
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=True,
                )
            )

    # model_versions active switch
    with op.batch_alter_table("model_versions") as batch_op:
        if not _has_column("model_versions", "is_active"):
            batch_op.add_column(
                sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true())
            )

    # ETL table
    if not _has_table("data_loads"):
        op.create_table(
            "data_loads",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("source", sa.String(length=100), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("rows_loaded", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )

    # Required indexes
    if not _has_index("sales", "ix_sales_sale_date"):
        op.create_index("ix_sales_sale_date", "sales", ["sale_date"])
    if not _has_index("forecasts", "ix_forecasts_target_date"):
        op.create_index("ix_forecasts_target_date", "forecasts", ["target_date"])
    if not _has_index("inventory", "ix_inventory_product_warehouse"):
        op.create_index("ix_inventory_product_warehouse", "inventory", ["product_id", "warehouse_id"])


def downgrade() -> None:
    if _has_index("inventory", "ix_inventory_product_warehouse"):
        op.drop_index("ix_inventory_product_warehouse", table_name="inventory")
    if _has_index("forecasts", "ix_forecasts_target_date"):
        op.drop_index("ix_forecasts_target_date", table_name="forecasts")
    if _has_index("sales", "ix_sales_sale_date"):
        op.drop_index("ix_sales_sale_date", table_name="sales")

    op.drop_table("data_loads")

    with op.batch_alter_table("model_versions") as batch_op:
        if _has_column("model_versions", "is_active"):
            batch_op.drop_column("is_active")

    with op.batch_alter_table("forecast_explanations") as batch_op:
        if _has_column("forecast_explanations", "created_at"):
            batch_op.drop_column("created_at")

    with op.batch_alter_table("sales") as batch_op:
        if _has_column("sales", "revenue"):
            batch_op.drop_column("revenue")
        batch_op.add_column(sa.Column("revenue", sa.Float(), nullable=True))

    op.drop_table("inventory_history")

    with op.batch_alter_table("forecasts") as batch_op:
        if _has_unique("forecasts", "uq_forecasts_product_warehouse_target_model"):
            batch_op.drop_constraint("uq_forecasts_product_warehouse_target_model", type_="unique")
        if _has_fk("forecasts", "fk_forecasts_item_id_items"):
            batch_op.drop_constraint("fk_forecasts_item_id_items", type_="foreignkey")
        if _has_fk("forecasts", "fk_forecasts_shop_id_shops"):
            batch_op.drop_constraint("fk_forecasts_shop_id_shops", type_="foreignkey")
        if not _has_column("forecasts", "month"):
            batch_op.add_column(sa.Column("month", sa.Date(), nullable=True))
        if not _has_column("forecasts", "predicted_cnt"):
            batch_op.add_column(sa.Column("predicted_cnt", sa.Float(), nullable=True))

    with op.batch_alter_table("monthly_sales") as batch_op:
        if _has_unique("monthly_sales", "uq_monthly_sales_shop_item_month"):
            batch_op.drop_constraint("uq_monthly_sales_shop_item_month", type_="unique")

    with op.batch_alter_table("features") as batch_op:
        if _has_unique("features", "uq_features_shop_item_month"):
            batch_op.drop_constraint("uq_features_shop_item_month", type_="unique")
        if _has_column("features", "month_num"):
            batch_op.drop_column("month_num")
        if _has_column("features", "price_trend"):
            batch_op.drop_column("price_trend")
        if _has_column("features", "rolling_mean_6"):
            batch_op.drop_column("rolling_mean_6")
        if _has_column("features", "lag_6"):
            batch_op.drop_column("lag_6")

    with op.batch_alter_table("warehouses") as batch_op:
        if _has_fk("warehouses", "fk_warehouses_shop_id_shops"):
            batch_op.drop_constraint("fk_warehouses_shop_id_shops", type_="foreignkey")
        if _has_column("warehouses", "shop_id"):
            batch_op.drop_column("shop_id")

    with op.batch_alter_table("products") as batch_op:
        if _has_fk("products", "fk_products_item_id_items"):
            batch_op.drop_constraint("fk_products_item_id_items", type_="foreignkey")
        if _has_column("products", "item_id"):
            batch_op.drop_column("item_id")
