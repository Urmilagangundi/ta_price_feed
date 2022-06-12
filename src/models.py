from flask import request, current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class PricingFeeds(db.Model):
    __tablename__ = 'pricing_feeds'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(), nullable=False)
    store_id = db.Column(db.Integer, nullable=False)
    sku = db.Column(db.String(), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    product_date = db.Column(db.Date, nullable=False)

    def __init__(self, product_name, store_id, sku, price, product_date):
        self.product_name = product_name
        self.store_id = store_id
        self.sku = sku
        self.price = price
        self.product_date = product_date

