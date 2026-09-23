import os, re
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from sqlalchemy import create_engine, String, DateTime, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from werkzeug.middleware.proxy_fix import ProxyFix

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///spingo.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

class Base(DeclarativeBase):
    pass

class Tester(Base):
    __tablename__ = "testers"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

Base.metadata.create_all(engine)

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))

@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.get("/style.css")
def style():
    return send_from_directory(BASE_DIR, "style.css")

@app.get("/screenshot-<int:number>.png")
def screenshot(number):
    if number not in (1, 2, 3):
        return "Not found", 404
    return send_from_directory(BASE_DIR, f"screenshot-{number}.png")

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    if not valid_email(email):
        return jsonify(ok=False, message="Entre une adresse e-mail valide."), 400

    with Session(engine) as db:
        existing = db.scalar(select(Tester).where(Tester.email == email))
        if existing:
            return jsonify(ok=True, message="Tu es déjà inscrit. Tu recevras les informations du test le 4 octobre. 🚀")

        db.add(Tester(email=email, created_at=datetime.now(timezone.utc)))
        db.commit()

    return jsonify(ok=True, message="Inscription confirmée ! Tu recevras le lien le 4 octobre. 🚀")

@app.get("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
