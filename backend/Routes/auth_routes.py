from flask import request
from flask_restx import Namespace, Resource, fields
from Services.auth_service import register, login
from Utils.Response import success_response, error_response
from database import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

 
auth_routes = Namespace("auth", description="authentication API")
user_model = auth_routes.model("User", {
                                        "user_name":fields.String(required=True), 
                                        "email":fields.String(required=True), 
                                        "password":fields.String(required=True),
                                        "role":fields.String(required=True)
                                        }
                               )
@auth_routes.route("/register", methods=["POST"])
class Register(Resource):
    @auth_routes.expect(user_model)
    def register():
        try:
            data = request.get_json()
            user = User.query.filter_by(user_name=data["user_name"]).first()
            
            if user:
                return error_response(
                    message="User already exist",
                    status_code=409
                )
            
            role = data.get("role", "user").lower()
            valid_roles = ["admin", "user", "manager", "nagu_bhai"]
            
            if role not in valid_roles:
                return error_response(
                    message="Role is not valid",
                    status_code=400
                )
                
            user = User(
                user_name = data["user_name"],
                email = data["email"],
                role = data["role"],
                password = generate_password_hash(data["password"])
            )
            
            db.session.add(user)
            db.session.commit()
            
            return success_response(
                message="New user added",
                data={
                    "name": data["user_name"],
                    "email": data["email"],
                    "role": data["role"]
                }
            )
        except Exception as e:
            return error_response(str(e))

    
login_model = auth_routes.model("Login", {
                                        "email":fields.String(required=True),
                                        "password":fields.String(required=True)
                                        })
@auth_routes.route("/login", methods=["POST"])    
class Login(Resource):
    @auth_routes.expect(login_model)
    def login(data):
        try:
            data = request.get_json()
            user_email = data["email"]
            
            if not user_email:
                return error_response(
                    message="Enter user email and password",
                    status_code=403
                )
                
            user = User.query.filter_by(email=user_email).first()
            
            if not user:
                return error_response(
                    message="User not exist, rigester first",
                    status_code=404
                )
            
            if user and check_password_hash(user.password, data["password"]):
                # session["id"] = user.id
                # session["role"] = user.role
                result = {
                    "id": user.id,
                    "name": user.user_name,
                    "email": user.email,
                    "role": user.role
                }
                return success_response(
                    message="Login successfull",
                    data=result
                )
            return error_response("Invalid username or password")
            
        except Exception as e:
            return error_response(str(e))
    