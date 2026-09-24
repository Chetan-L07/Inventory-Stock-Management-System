from database import db
from datetime import datetime

#  User table
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    sign_up_time = db.Column(db.DateTime, default=datetime.utcnow) 
    role = db.Column(db.String(300), nullable=False, default="user")
        

    