from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

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

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True, nullable=False)
    month = Column(Date, index=True, nullable=False)
    item_cnt_month = Column(Float, nullable=False, default=0.0)


class FeatureRow(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True, nullable=False)
    month = Column(Date, index=True, nullable=False)
    lag_1 = Column(Float, nullable=True)
    lag_3 = Column(Float, nullable=True)
    lag_12 = Column(Float, nullable=True)
    rolling_mean_3 = Column(Float, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=True)
    year = Column(Integer, nullable=True)
    item_price = Column(Float, nullable=True)
    seasonal_flag = Column(Integer, nullable=True)


class TestData(Base):
    __tablename__ = "test_data"

    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey("shops.shop_id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.item_id"), index=True, nullable=False)
