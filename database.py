import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from models import MenuItem
import json
import pathlib
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///orders.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def refresh_menu_cache():
    """Rebuilds a JSON cache of active menu items for the bot to consume.

    The cache is written to `static/menu_cache.json` and contains a list of
    items with keys: id, category, name, bangla (list), aliases (list), price.
    """
    db = SessionLocal()
    try:
        items = (
            db.query(MenuItem)
            .filter(MenuItem.active == 1)
            .order_by(MenuItem.name)
            .all()
        )

        out = []
        for it in items:
            try:
                bangla = json.loads(it.bangla) if it.bangla else []
            except Exception:
                bangla = []
            try:
                aliases = json.loads(it.aliases) if it.aliases else []
            except Exception:
                aliases = []

            out.append(
                {
                    "id": it.id,
                    "category": it.category,
                    "name": it.name,
                    "bangla": bangla,
                    "aliases": aliases,
                    "price": it.price,
                }
            )

        path = pathlib.Path("static")
        path.mkdir(parents=True, exist_ok=True)
        cache_file = path / "menu_cache.json"
        with cache_file.open("w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    finally:
        db.close()
