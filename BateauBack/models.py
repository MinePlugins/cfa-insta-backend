from . import db
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(6), nullable=False)
    availability = db.Column(db.Boolean, nullable=False)
    sale = db.Column(db.Boolean, nullable=False)
    discount = db.Column(db.Float, nullable=False)
    comments = db.Column(db.String(254))
    owner = db.Column(db.String(254))
    quantity_sales = db.Column(db.Integer)
    stock = db.Column(db.Integer)

    def __repr__(self):
        return '<Product %r>' % self.name

class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        include_fk = True

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    products = db.relationship("Product", backref='cat', lazy=True)

    def __repr__(self):
        return '<Category %r>' % self.name

class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        include_fk = True