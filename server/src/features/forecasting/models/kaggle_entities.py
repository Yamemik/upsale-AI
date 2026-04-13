from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, UniqueConstraint

from src.db.base import Base


class Shop(Base):
    __tablename__ = "shops"

    shop_id = Column(Integer, primary_key=True)
    shop_name = Column(String, nullable=False)


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False, index=True)


class MonthlySale(Base):
    __tablename__ = "monthly_sales"
    __table_args__ = (
        UniqueConstraint("shop_id", "item_id", "month", name="uq_monthly_sales_shop_item_month"),
    )

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True, nullable=False)
    month = Column(Date, index=True, nullable=False)
    item_cnt_month = Column(Numeric(12, 3), nullable=False, default=0)


class FeatureRow(Base):
    __tablename__ = "features"
    __table_args__ = (
        UniqueConstraint("shop_id", "item_id", "month", name="uq_features_shop_item_month"),
    )

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True, nullable=False)
    month = Column(Date, index=True, nullable=False)
    lag_1 = Column(Numeric(12, 3), nullable=True)
    lag_3 = Column(Numeric(12, 3), nullable=True)
    lag_6 = Column(Numeric(12, 3), nullable=True)
    lag_12 = Column(Numeric(12, 3), nullable=True)
    rolling_mean_3 = Column(Numeric(12, 3), nullable=True)
    rolling_mean_6 = Column(Numeric(12, 3), nullable=True)
    price_trend = Column(Numeric(12, 6), nullable=True)
    month_num = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    year = Column(Integer, nullable=True)
    item_price = Column(Numeric(14, 2), nullable=True)
    seasonal_flag = Column(Integer, nullable=True)


class TestData(Base):
    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True, nullable=False)
