from flask import request
from flask_restx import Namespace, Resource, fields
from Utils.Response import success_response, error_response
from database import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_routes = Namespace("auth", description="Authentication API")

user_register_model = auth_routes.model(
    "UserRegister",
    {
        "user_name": fields.String(required=True, description="Unique username"),
        "email": fields.String(required=True, description="User email address"),
        "password": fields.String(required=True, description="Account password"),
        "role": fields.String(required=False, default="user", description="admin, user, manager, nagu_bhai"),
    },
)

user_login_model = auth_routes.model(
    "UserLogin",
    {
        "email": fields.String(required=True, description="Registered email address"),
        "password": fields.String(required=True, description="Account password"),
    },
)


def serialize_user(user):
    """Helper to convert User model into JSON-ready dict"""
    return {
        "id": user.id,
        "name": user.user_name,
        "email": user.email,
        "role": user.role,
        "sign_up_time": str(user.sign_up_time) if hasattr(user, "sign_up_time") else None,
    }


@auth_routes.route("/register")
class Register(Resource):

    # 1. USER REGISTRATION
    @auth_routes.expect(user_register_model)
    def post(self):
        try:
            data = request.get_json()

            user_name = data.get("user_name", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password")
            role = data.get("role", "user").strip().lower()

            if not user_name or not email or not password:
                return error_response(
                    message="Username, email, and password are required",
                    status_code=400,
                )

            existing_user = User.query.filter_by(user_name=user_name).first()
            if existing_user:
                return error_response(
                    message="Username already exists",
                    status_code=409,
                )

            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                return error_response(
                    message="Email already registered",
                    status_code=409,
                )

            valid_roles = ["admin", "user", "manager", "nagu_bhai"]
            if role not in valid_roles:
                return error_response(
                    message=f"Role is not valid. Choose from: {', '.join(valid_roles)}",
                    status_code=400,
                )

            new_user = User(
                user_name=user_name,
                email=email,
                role=role,
                password=generate_password_hash(password),
            )

            db.session.add(new_user)
            db.session.commit()

            return success_response(
                message="User registered successfully",
                data=serialize_user(new_user),
            )
        except Exception as e:
            db.session.rollback()
            return error_response(str(e))


@auth_routes.route("/login")
class Login(Resource):

    # 2. USER LOGIN
    @auth_routes.expect(user_login_model)
    def post(self):
        try:
            data = request.get_json()

            user_email = data.get("email", "").strip()
            password = data.get("password")

            if not user_email or not password:
                return error_response(
                    message="Email and password are required",
                    status_code=400,
                )

            user = User.query.filter_by(email=user_email).first()
            if not user:
                return error_response(
                    message="User does not exist, register first",
                    status_code=404,
                )

            if check_password_hash(user.password, password):
                return success_response(
                    message="Login successful",
                    data=serialize_user(user),
                )

            return error_response(
                message="Invalid email or password",
                status_code=401,
            )
        except Exception as e:
            return error_response(str(e))