from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from config import config
from database import db

# Routes
from Routes.auth_routes import auth_routes
from Routes.product_routes import product_routes
from Routes.category_routes import category_routes

from models import User
from models import Category
from models import Product

app = Flask(__name__)
CORS(app)

app.config.from_object(config)
app.secret_key = "chetan_project_nagu_bhai"
db.init_app(app)

with app.app_context():
    db.create_all()

api = Api(
    app,
    title="Inventory Management API",
    version="1.0",
    description="A simple inventory management system",
    doc="/swagger",
    prefix="/api/v1",
)
api.add_namespace(auth_routes, path="/auth")
api.add_namespace(product_routes, path="/products")
api.add_namespace(category_routes, path="/categories")

@app.route("/")
def home():
    return "<h1>Chetan_Loves_Nagu🐍</h1>"


if __name__ == "__main__":
    app.run(debug = True, port=5001, use_reloader=False)