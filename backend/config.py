import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class config:
    # 1. Cloud-native DATABASE_URL (Supported by Supabase, Neon, Render, Railway, etc.)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # SQLAlchemy requires postgresql:// instead of postgres://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # 2. Individual MySQL environment variables
        db_user = os.getenv("DB_USER")
        db_host = os.getenv("DB_HOST", "localhost")
        db_password = quote_plus(os.getenv("DB_PASSWORD")) if os.getenv("DB_PASSWORD") else ""
        db_port = os.getenv("DB_PORT", "3306")
        db_database = os.getenv("DB_NAME")

        if db_user and db_database:
            SQLALCHEMY_DATABASE_URI = (
                f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
            )
        else:
            # 3. Default fallback to local SQLite
            base_dir = os.path.abspath(os.path.dirname(__file__))
            db_dir = os.path.join(base_dir, "..", "Database")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "inventory.db")
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

