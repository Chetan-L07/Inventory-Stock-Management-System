from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from config import config
from database import db

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
    title="inventory management API",
    description="a simple inventory management system",
    doc="/swagger",
    prefix="/api/v1",
)


@app.route("/")
def home():
    return "<h1>Chetan_Loves_Nagu🐍</h1>"


if __name__ == "__main__":
    app.run(debug = True, port=5001, use_reloader=False)