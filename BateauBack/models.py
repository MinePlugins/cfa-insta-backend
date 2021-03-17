from . import db
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, fields
from marshmallow import post_load
import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    availability = db.Column(db.Boolean, nullable=False)
    sale = db.Column(db.Boolean, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    comments = db.Column(db.String(254))
    owner = db.Column(db.String(254))
    quantity_sales = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    image = db.Column(db.String())
    history = db.relationship("ProductHistory", uselist=False, back_populates="products")
    def __repr__(self):
        return '<Product %r>' % self.name

class ProductHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    products = db.relationship("Product", back_populates='history')
    products_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    datetime = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    purshase_price = db.Column(db.Float)
    sell_price = db.Column(db.Float)
    stock_change = db.Column(db.Float)
    promotion_percent = db.Column(db.Integer)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship("Product", backref='category', lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name

class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
        sqla_session = db.session
        include_fk = True

class ProductHistorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProductHistory
        load_instance = True
        sqla_session = db.session
        include_fk = True

class ProductSchema(SQLAlchemyAutoSchema):
    category = fields.Nested(CategorySchema, data_key="category")
    class Meta:
        model = Product
        load_instance = True
        sqla_session = db.session
        include_fk = True


