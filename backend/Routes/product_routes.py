from flask import request
from flask_restx import Namespace, Resource, fields
from Utils.Response import success_response, error_response
from database import db
from models import Product, Category

product_routes = Namespace("products", description="Product management API")

product_create_model = product_routes.model(
    "ProductCreate",
    {
        "name": fields.String(required=True, description="Product title"),
        "barcode": fields.String(required=False, description="UPC or Barcode"),
        "category_id": fields.Integer(required=False, description="Category ID"),
        "cost_price": fields.Float(required=True, description="Cost price"),
        "selling_price": fields.Float(required=True, description="Selling price"),
        "stock_quantity": fields.Integer(required=True, description="Available stock"),
        "min_stock_level": fields.Integer(required=False, default=5, description="Low stock warning alert threshold"),
        "unit": fields.String(required=False, default="pcs", description="Unit of measurement"),
    },
)

product_update_model = product_routes.model(
    "ProductUpdate",
    {
        "name": fields.String(required=False),
        "barcode": fields.String(required=False),
        "category_id": fields.Integer(required=False),
        "cost_price": fields.Float(required=False),
        "selling_price": fields.Float(required=False),
        "stock_quantity": fields.Integer(required=False),
        "min_stock_level": fields.Integer(required=False),
        "unit": fields.String(required=False),
    },
)


def serialize_product(product):
    """Helper to convert product model into JSON-ready dict"""
    return {
        "id": product.id,
        "name": product.name,
        "barcode": product.barcode,
        "category_id": product.category_id,
        "category_name": product.category.name if product.category else None,
        "cost_price": float(product.cost_price),
        "selling_price": float(product.selling_price),
        "stock_quantity": product.stock_quantity,
        "min_stock_level": product.min_stock_level,
        "unit": product.unit,
        "created_at": str(product.created_at),
        "updated_at": str(product.updated_at),
    }


@product_routes.route("")
class ProductListCreate(Resource):

    # 1. SHOW ALL PRODUCTS
    def get(self):
        try:
            products = Product.query.order_by(Product.id.desc()).all()
            result = [serialize_product(p) for p in products]

            return success_response(
                message="Products retrieved successfully", 
                data=result
            )
        except Exception as e:
            return error_response(str(e))

    # 2. ADD A NEW PRODUCT
    @product_routes.expect(product_create_model)
    def post(self):
        try:
            data = request.get_json()

            # Check barcode uniqueness if barcode provided
            barcode = data.get("barcode")
            if barcode:
                existing_product = Product.query.filter_by(barcode=barcode).first()
                if existing_product:
                    return error_response(
                        message="Product with this barcode already exists",
                        status_code=409,
                    )

            # Validate category if category_id passed
            category_id = data.get("category_id")
            if category_id:
                category = Category.query.get(category_id)
                if not category:
                    return error_response(
                        message="Category not found", 
                        status_code=404
                    )

            new_product = Product(
                name=data["name"],
                barcode=barcode,
                category_id=category_id,
                cost_price=data["cost_price"],
                selling_price=data["selling_price"],
                stock_quantity=data.get("stock_quantity", 0),
                min_stock_level=data.get("min_stock_level", 5),
                unit=data.get("unit", "pcs"),
            )

            db.session.add(new_product)
            db.session.commit()

            return success_response(
                message="Product added successfully",
                data=serialize_product(new_product),
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))


@product_routes.route("/<int:product_id>")
class ProductDetailUpdateDelete(Resource):

    # 3. UPDATE EXISTING PRODUCT
    @product_routes.expect(product_update_model)
    def put(self, product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return error_response(
                    message="Product not found", 
                    status_code=404
                )

            data = request.get_json()

            # Check barcode conflict if being changed
            barcode = data.get("barcode")
            if barcode and barcode != product.barcode:
                existing = Product.query.filter_by(barcode=barcode).first()
                if existing:
                    return error_response(
                        message="Barcode already assigned to another product",
                        status_code=409,
                    )
                product.barcode = barcode

            # Check category if being updated
            if "category_id" in data:
                category_id = data["category_id"]
                if category_id is not None:
                    category = Category.query.get(category_id)
                    if not category:
                        return error_response(
                            message="Category not found", 
                            status_code=404
                        )
                product.category_id = category_id

            # Update remaining fields if provided
            if "name" in data:
                product.name = data["name"]
            if "cost_price" in data:
                product.cost_price = data["cost_price"]
            if "selling_price" in data:
                product.selling_price = data["selling_price"]
            if "stock_quantity" in data:
                product.stock_quantity = data["stock_quantity"]
            if "min_stock_level" in data:
                product.min_stock_level = data["min_stock_level"]
            if "unit" in data:
                product.unit = data["unit"]

            db.session.commit()

            return success_response(
                message="Product updated successfully",
                data=serialize_product(product),
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    # 4. REMOVE PRODUCT
    def delete(self, product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return error_response(
                    message="Product not found", 
                    status_code=404
                )

            db.session.delete(product)
            db.session.commit()

            return success_response(
                message="Product removed successfully",
                data={"deleted_product_id": product_id},
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))