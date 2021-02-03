import datetime
from sqlalchemy import Column, SmallInteger, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from app.utils.type_checker import check_batch_type


class CustomerInteraction:
    def __init__(self, product_id: int, customer_id: int, date: datetime, views: int, purchases: int, add_to_cart: int,
                 add_to_wishlist: int, time_on_page: float, last_updated_date: datetime):
        check_batch_type([
            [product_id, int],
            [customer_id, int],
            [views, int],
            [purchases, int],
            [add_to_cart, int],
            [add_to_wishlist, int],
            [time_on_page, float],
        ])
        if date.__class__.__name__ != 'datetime':
            raise RuntimeError(f'Wrong type for last_updated_at {date.__class__.__name__}')
        if last_updated_date.__class__.__name__ != 'datetime':
            raise RuntimeError(f'Wrong type for last_updated_at {last_updated_date.__class__.__name__}')
        self.product_id = product_id
        self.customer_id = customer_id
        self.date = date
        self.views = views
        self.purchases = purchases
        self.add_to_cart = add_to_cart
        self.add_to_wishlist = add_to_wishlist
        self.time_on_page = time_on_page
        self.last_updated_date = last_updated_date


Base = declarative_base()


class CustomerInteractionTable(Base):
    __tablename__ = "customer_interaction"
    customer_id = Column('customer_id', Integer, primary_key=True)
    product_id = Column('product_id', Integer, primary_key=True)
    date = Column('date', Date)  # Date of interaction
    brand_id = Column('brand_id', Integer, nullable=False)
    gender = Column('gender', SmallInteger, nullable=False)  # 0 Women 1 Men
    views = Column('views', SmallInteger, nullable=False)  # number of page views
    purchased = Column('purchased', Integer)
    add_to_cart = Column('add_to_cart', SmallInteger, nullable=False)  # quantity of item added to cart
    add_to_wishlist = Column('add_to_wishlist', SmallInteger, nullable=False)  # quantity of item added to wish-list
    time_on_page = Column('time_on_page', Float, nullable=False)
