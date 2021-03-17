from flask_restful import Resource, reqparse
from .. import app, RestAPI, db
from .. import Product, Category, ProductSchema, CategorySchema, ProductHistory, ProductHistorySchema
import requests, json
from sqlalchemy import func
from ..auth import auth_required, admin_required
from flask import request
from distutils.util import strtobool
import datetime
import re 

def duration(string):
    mult = {"s": 1, "m": 60, "h": 60*60, "d": 60*60*24, "w": 60*60*24*7, "l": 60*60*24*30, "y": 60*60*24*365}
    parts = re.findall(r"(\d+(?:\.\d)?)([smhdwly])", string)
    total_seconds = sum(float(x) * mult[m] for x, m in parts)
    return datetime.timedelta(seconds=total_seconds)

def get_category_from_id(id):
    return Category.query.filter_by(id=id).first()

def get_category_from_name(name):
    return Category.query.filter_by(name=name).first()

def get_product_from_id(id):
    return Product.query.filter_by(id=id).first()

category_parser = reqparse.RequestParser()
category_parser.add_argument('name')

parser_product = reqparse.RequestParser()
parser = reqparse.RequestParser()
parser_sale = reqparse.RequestParser()

def stock_apply(id, types,quantity, price, message=False):
    product = Product.query.filter(Product.id==id).first()
    product_id = product
    quantity = int(quantity)
    price = float(price)
    if product.stock == None:
        product.stock = 0
    if types == "in":
        product.stock = product.stock + quantity
        history = ProductHistory(
            products=product_id,
            stock_change=quantity,
            purshase_price=price
        )
    elif types == "out":
        if product.stock - quantity >= 0:
            product.stock = product.stock - quantity
        else:
            if message:
                return 'La quantité ne peux être négative'
            else:
                return {'message': 'La quantité ne peux être négative'}, 406
        history = ProductHistory(
            products=product_id,
            stock_change=quantity,
            sell_price=price
        )
    elif types == "loss":
        history = ProductHistory(
            products=product_id,
            stock_change=quantity
        )
    if product.stock == 0:
        product.availability = False
    else:
        product.availability = True
    db.session.add(history)
    db.session.commit()
    if message:
        return 'Mise à jour du stock avec succès'
    else:
        return {'message': 'Mise à jour du stock avec succès'}, 200

        
def promo_apply(id, sale, message=False):
    product = Product.query.filter(Product.id==id).first()
    if product.price == None:
        product.price = 0
    if sale < 0 or sale > 100:
        if message:
            return "Le pourcentage appliqué ne peux être contenue en dehors de 0 et 100"
        else:
            return {'message': 'Le pourcentage appliqué ne peux être contenue en dehors de 0 et 100'}, 406
    if sale == 0:
        product.discount = 0
    else:
        cal =  (sale/100) * product.price
        product.discount = product.price - cal
    if product.discount == 0:
        product.sale = False
    else:
        product.sale = True
    db.session.commit()
    if message:
        return "Mise à jour de la promo"
    else:
        return {'message': 'Mise à jour de la promo'}, 200


class ProductView(Resource):
    # @auth_required
    def get(self, id):

        product = Product.query.filter_by(id=id).first()
        schema = ProductSchema()
        if product:
            return schema.dump(product)
        else:
            return {'error': 'Not found'}, 404

    def patch(self, id):
        parser_product.add_argument('name', required=True, location='json', type=str,
            help="Must have a correct name.")
        parser_product.add_argument('price', required=True, location='json', type=float,
            help="Must have a correct price.")
        parser_product.add_argument('unit', required=True, location='json', type=str,
            help="Must have a correct unit.")
        parser_product.add_argument('availability', required=True, location='json', type=bool,
            help="Must have a correct availability.")
        parser_product.add_argument('sale', required=True, location='json', type=bool,
            help="Must have a correct sale.")
        parser_product.add_argument('discount', required=True, location='json', type=float,
            help="Must have a correct discount.")
        parser_product.add_argument('comments', required=True, location='json', type=str,
            help="Must have a correct comments.")
        parser_product.add_argument('owner', required=True, location='json', type=str,
            help="Must have a correct owner.")
        parser_product.add_argument('stock', required=False, location='json', type=int,
            help="Must have a correct stock.")
        parser_product.add_argument('category', required=True,location='json',
            help="Must have a correct category.")
        parser_product.parse_args()
        try:
            args = request.get_json()
            message = ""
            if "promo" in args:
                message = promo_apply(id, int(args['promo']), True)
                del args["promo"]
                del args["discount"]
            schema = ProductSchema()
            data = schema.load(args, partial=True, instance=Product.query.filter(Product.id==id).first())
            db.session.commit()
            return {'message': 'Mise à jour avec succés et {}'.format(message)}, 200
        except Exception as e:
            print(e)
            return {'message': "Une erreur est survenu"}, 404

class CategoriesView(Resource):
    @auth_required
    def get(self):
        categories = Category.query.all()
        schema = CategorySchema(many=True)

        if categories:
            return schema.dump(categories)
        else:
            return {'error': 'Not found'}, 404

class CategoryView(Resource):
    @auth_required
    def get(self, id):
        category = Category.query.filter_by(id=id).first()
        schema = CategorySchema()
        if category:
            return schema.dump(category)
        else:
            return {'error': 'Not found'}, 404

class CreateCategoryView(Resource):
    def post(self):
        args = category_parser.parse_args()
        name = args['name']
        category = get_category_from_name(name)
        if category:
            return {'error': 'Category already exist'}, 409
        else:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit()
            return {'success': 'The category has been added'}, 200



class ProductsView(Resource):
    def get(self):
        products = Product.query.all()
        schema = ProductSchema(many=True)
        if products:
            return schema.dump(products)
        else:
            return {'error': 'Not found'}, 404

class ProductsSearchView(Resource):
    def get(self, name):
        print(name)
        products = Product.query.filter(Product.name.like('%' + name + '%')).all()
        print(products)

        schema = ProductSchema(many=True)
        if products:
            return schema.dump(products)
        else:
            return {'error': 'Not found'}, 404

class ProductsSyncView(Resource):
    def get(self):
        products = requests.get("http://51.255.166.155:1352/tig/products/?format=json")
        products = products.json()
        results = []
        for product in products:
            print(product["id"])
            category = get_category_from_id(product["category"]+1)
            product_exist = get_product_from_id(product["id"])
            print(product_exist)
            if product_exist is None:
                if category:
                    new_product = Product(  id=product["id"],
                                            cat=category,
                                            name=product["name"],
                                            price=product["price"],
                                            unit=product["unit"],
                                            sale=product["sale"],
                                            availability=product["availability"],
                                            discount=product["discount"],
                                            comments=product["comments"],
                                            owner=product["owner"],
                                        )
                    db.session.add(new_product)
                    db.session.commit()
                    results.append({'success': '{} product added to database'.format(product["name"])})
                else:
                    results.append({'error': 'Category of product {} not found'.format(product["name"])})
            else:
                results.append({'error': 'Product {} already exist'.format(product["name"])})

        return results, 200

class ProductStockIncrDecr(Resource):
    @auth_required
    def patch(self, id):
        parser.add_argument('quantity', required=True, location='json', type=int,
            help="Must have a correct quantity.")
        parser.add_argument('types', required=True, location='json', type=str,
            help="Must have a correct method.")
        parser.add_argument('price', required=False, location='json', type=str,
            help="Must have a correct method.")
        try:
            args = parser.parse_args()
            return stock_apply(id,args['types'], args['quantity'],args['price'])
        except Exception as e:
            print(e)
            return {'message': 'Une erreur est survenu'}, 404

class ProductSaleSet(Resource):
    @auth_required
    def patch(self, id):
        parser_sale.add_argument('sale', required=True, location='json', type=int,
            help="Must have a correct sale percent.")
        try:
            args = parser_sale.parse_args()
            return promo_apply(id, args['sale'])
        except Exception as e:
            print(e)
            return {'message': 'Une erreur est survenu'}, 404


class CA(Resource):
    # @auth_required
    def get(self, datediff, category="all"):
        duration_delta = duration(datediff)
        now_minus_timedelta = datetime.datetime.now() - duration_delta
        print(now_minus_timedelta)
        if category == "all":
            history = ProductHistory.query.filter(ProductHistory.datetime > now_minus_timedelta).all()
        else:
            category = int(category)
            history = ProductHistory.query.join(Product).join(Category).filter(ProductHistory.datetime > now_minus_timedelta,
                Product.category_id == category).all()
        schema = ProductHistorySchema(many=True)
        return schema.dump(history)


RestAPI.add_resource(CA, '/api/history/<string:datediff>/<string:category>')
RestAPI.add_resource(ProductView, '/api/product/<int:id>')
RestAPI.add_resource(ProductStockIncrDecr, '/api/productstock/<int:id>')
RestAPI.add_resource(ProductSaleSet, '/api/productsale/<int:id>')
RestAPI.add_resource(ProductsSearchView, '/api/searchproduct/<string:name>')
RestAPI.add_resource(ProductsView, '/api/products/')
RestAPI.add_resource(ProductsSyncView, '/api/productsync/')
RestAPI.add_resource(CreateCategoryView, '/api/category/')
RestAPI.add_resource(CategoriesView, '/api/categories/')
RestAPI.add_resource(CategoryView, '/api/category/<int:id>')
