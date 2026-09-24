from flask import request
from flask_restx import Namespace, Resource, fields
from Utils.Response import success_response, error_response
from database import db
from models import Category

category_routes = Namespace("categories", description="Category management API")

category_model = category_routes.model(
    "Category",
    {
        "name": fields.String(required=True, description="Category name (e.g., Snacks, Dairy, Beverages)")
    },
)


def serialize_category(cat):
    """Helper to convert Category object to a clean dict"""
    return {
        "id": cat.id,
        "name": cat.name,
        "total_products": len(cat.products) if cat.products else 0,
        "created_at": str(cat.created_at),
    }


@category_routes.route("")
class CategoryListCreate(Resource):

    # 1. GET ALL CATEGORIES
    def get(self):
        try:
            categories = Category.query.order_by(Category.name.asc()).all()
            result = [serialize_category(cat) for cat in categories]

            return success_response(
                message="Categories retrieved successfully",
                data=result,
            )
        except Exception as e:
            return error_response(str(e))

    # 2. CREATE A CATEGORY
    @category_routes.expect(category_model)
    def post(self):
        try:
            data = request.get_json()
            name = data.get("name", "").strip()

            if not name:
                return error_response(
                    message="Category name is required",
                    status_code=400,
                )
                
            existing = Category.query.filter(Category.name.ilike(name)).first()
            if existing:
                return error_response(
                    message=f"Category '{name}' already exists",
                    status_code=409,
                )

            new_category = Category(name=name)
            db.session.add(new_category)
            db.session.commit()

            return success_response(
                message="Category created successfully",
                data=serialize_category(new_category),
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))


@category_routes.route("/<int:category_id>")
class CategoryDetailUpdateDelete(Resource):

    # 3. GET A SINGLE CATEGORY BY ID
    def get(self, category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return error_response(
                    message="Category not found",
                    status_code=404,
                )

            return success_response(
                message="Category retrieved successfully",
                data=serialize_category(category),
            )
        except Exception as e:
            return error_response(str(e))

    # 4. UPDATE A CATEGORY
    @category_routes.expect(category_model)
    def put(self, category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return error_response(
                    message="Category not found",
                    status_code=404,
                )

            data = request.get_json()
            new_name = data.get("name", "").strip()

            if not new_name:
                return error_response(
                    message="Category name cannot be empty",
                    status_code=400,
                )

            existing = Category.query.filter(
                Category.name.ilike(new_name),
                Category.id != category_id
            ).first()

            if existing:
                return error_response(
                    message=f"Category name '{new_name}' is already in use",
                    status_code=409,
                )

            category.name = new_name
            db.session.commit()

            return success_response(
                message="Category updated successfully",
                data=serialize_category(category),
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))

    # 5. DELETE A CATEGORY
    def delete(self, category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return error_response(
                    message="Category not found",
                    status_code=404,
                )

            db.session.delete(category)
            db.session.commit()

            return success_response(
                message="Category removed successfully",
                data={"deleted_category_id": category_id},
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))