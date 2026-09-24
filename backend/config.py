from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()


class config:
    db_user = os.getenv("DB_USER")
    db_host = os.getenv("DB_HOST")
    db_password = quote_plus(os.getenv("DB_PASSWORD"))
    db_port = os.getenv("DB_PORT")
    db_database = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
