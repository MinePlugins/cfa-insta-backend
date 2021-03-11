from flask_restful import Resource, reqparse
from .. import app, RestAPI, db
from .. import Product, Category, ProductSchema, CategorySchema
import requests, json

def get_category_from_id(id):
    return Category.query.filter_by(id=id).first()

def get_category_from_name(name):
    return Category.query.filter_by(name=name).first()

def get_product_from_id(id):
    return Product.query.filter_by(id=id).first()

category_parser = reqparse.RequestParser()
category_parser.add_argument('name')

class ProductView(Resource):
    def get(self, id):
        product = Product.query.filter_by(id=id).first()
        schema = ProductSchema()
        if product:
            return schema.dump(product)
        else:
            return {'error': 'Not found'}, 404

class CategoriesView(Resource):
    def get(self):
        categories = Category.query.all()
        schema = CategorySchema(many=True)

        if categories:
            return {"categories": schema.dump(categories)}
        else:
            return {'error': 'Not found'}, 404

class CategoryView(Resource):
    def get(self, id):
        category = Category.query.filter_by(id=id).first()
        schema = CategorySchema()
        if category:
            return {"category": schema.dump(category)}
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


RestAPI.add_resource(ProductView, '/api/product/<int:id>')
RestAPI.add_resource(ProductsView, '/api/products/')
RestAPI.add_resource(ProductsSyncView, '/api/productsync/')
RestAPI.add_resource(CreateCategoryView, '/api/category/')
RestAPI.add_resource(CategoriesView, '/api/categories/')
RestAPI.add_resource(CategoryView, '/api/category/<int:id>')
