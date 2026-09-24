from database import db
from Utils.Response import error_response, success_response
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

def rigester(data):
    try:
        user = User.query.filter_by(name=data["name"]).first()
        
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
            name = data["name"],
            email = data["email"],
            role = data["role"],
            password = generate_password_hash(data["password"])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return success_response(
            message="New user added",
            data={
                "name": data["name"],
                "email": data["email"],
                "role": data["role"]
            }
        )
    except Exception as e:
        return error_response(str(e))
    
def login(data):
    try:
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
                "name": user.name,
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