import csv
import hmac
import io
import os
import re
from datetime import datetime, timezone

from flask import Flask, Response, jsonify, redirect, render_template_string, request, session, send_from_directory
from sqlalchemy import create_engine, String, DateTime, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from werkzeug.middleware.proxy_fix import ProxyFix

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///spingo.db")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

# Render peut fournir une URL PostgreSQL sans pilote explicite.
# On force psycopg (v3), installé dans requirements.txt.
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
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-only-change-this")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True,
)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def valid_email(email):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def admin_logged_in():
    return session.get("admin_authenticated") is True


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


ADMIN_CSS = """
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#08080d;color:#f7f7fb;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}.wrap{width:min(1050px,calc(100% - 32px));margin:0 auto}.top{padding:28px 0;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #ffffff12}.brand{font-weight:900;font-size:20px}.brand span{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:10px;background:linear-gradient(135deg,#8b5cf6,#a855f7);margin-right:9px}.muted{color:#8b8b98}.btn{border:1px solid #ffffff18;background:#ffffff08;color:#fff;text-decoration:none;border-radius:11px;padding:10px 14px;font-weight:800;cursor:pointer}.btn.primary{background:linear-gradient(135deg,#8b5cf6,#a855f7);border:0}.main{padding:55px 0 80px}.eyebrow{color:#bfa4ff;font-size:12px;font-weight:900;letter-spacing:1.4px;text-transform:uppercase}.title{font-size:clamp(38px,6vw,62px);line-height:1;margin:10px 0 10px;letter-spacing:-2px}.cards{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin:30px 0}.card{border:1px solid #ffffff12;background:linear-gradient(145deg,#15151d,#0e0e13);border-radius:18px;padding:22px}.number{font-size:32px;font-weight:950}.table-wrap{overflow:auto;border:1px solid #ffffff12;border-radius:18px;background:#0d0d13}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:25px 0 12px}.toolbar h2{margin:0;font-size:21px}.table{width:100%;border-collapse:collapse;min-width:650px}.table th,.table td{text-align:left;padding:15px 17px;border-bottom:1px solid #ffffff0d}.table th{font-size:12px;text-transform:uppercase;letter-spacing:.8px;color:#8d8d99}.table td{font-size:14px}.table tr:last-child td{border-bottom:0}.login{min-height:100vh;display:grid;place-items:center;padding:24px}.loginbox{width:min(430px,100%);border:1px solid #ffffff15;background:linear-gradient(145deg,#17131f,#0d0d13);border-radius:24px;padding:32px;box-shadow:0 30px 90px #000}.loginbox h1{margin:8px 0 10px;font-size:34px}.loginbox p{color:#9999a6;line-height:1.5}.field{display:block;margin:24px 0 10px;font-size:14px;font-weight:800}.input{width:100%;padding:14px;border-radius:11px;border:1px solid #ffffff18;background:#08080c;color:white;font-size:16px;outline:none}.input:focus{border-color:#9f76ff}.full{width:100%;margin-top:12px}.error{color:#ff9a9a;background:#ff00000d;border:1px solid #ff000033;padding:10px 12px;border-radius:10px;font-size:13px}.empty{padding:35px;text-align:center;color:#8b8b98}@media(max-width:650px){.cards{grid-template-columns:1fr}.top{gap:12px}.toolbar{align-items:flex-start;flex-direction:column}.main{padding-top:35px}}
"""


LOGIN_HTML = """<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>SpinGO — Admin</title><style>{{ css }}</style></head><body><main class='login'><section class='loginbox'><div class='eyebrow'>SPINGO • ADMIN</div><h1>Espace privé 🔐</h1><p>Connecte-toi pour voir les inscriptions au test SpinGO.</p>{% if error %}<div class='error'>{{ error }}</div>{% endif %}<form method='post'><label class='field' for='password'>Mot de passe administrateur</label><input class='input' id='password' name='password' type='password' autocomplete='current-password' required autofocus><button class='btn primary full' type='submit'>Se connecter →</button></form></section></main></body></html>"""


ADMIN_HTML = """<!doctype html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>SpinGO — Inscriptions</title><style>{{ css }}</style></head><body><header class='top'><div class='wrap' style='display:flex;justify-content:space-between;align-items:center;width:100%'><div class='brand'><span>S</span> SpinGO <span style='background:none;width:auto;margin:0;color:#8b8b98;font-size:12px'>ADMIN</span></div><a class='btn' href='/admin/logout'>Se déconnecter</a></div></header><main class='wrap main'><div class='eyebrow'>TEST PRIVÉ • 4 OCTOBRE 2026</div><h1 class='title'>Inscriptions</h1><p class='muted'>Voici les personnes inscrites au test privé de SpinGO.</p><div class='cards'><div class='card'><div class='number'>{{ count }}</div><div class='muted'>testeurs inscrits</div></div><div class='card'><div class='number'>14 jours</div><div class='muted'>durée minimale du test</div></div></div><div class='toolbar'><h2>Adresses e-mail</h2><a class='btn primary' href='/admin/export.csv'>📥 Télécharger le CSV</a></div><div class='table-wrap'>{% if testers %}<table class='table'><thead><tr><th>#</th><th>E-mail</th><th>Inscrit le</th></tr></thead><tbody>{% for tester in testers %}<tr><td>{{ tester.id }}</td><td>{{ tester.email }}</td><td>{{ tester.created_at.strftime('%d/%m/%Y à %H:%M') if tester.created_at else '—' }}</td></tr>{% endfor %}</tbody></table>{% else %}<div class='empty'>Aucun testeur inscrit pour le moment.</div>{% endif %}</div></main></body></html>"""


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not ADMIN_PASSWORD:
        return "ADMIN_PASSWORD n'est pas configuré sur le serveur.", 503

    if admin_logged_in():
        with Session(engine) as db:
            testers = db.scalars(select(Tester).order_by(Tester.id.desc())).all()
            count = db.scalar(select(func.count()).select_from(Tester)) or 0
        return render_template_string(ADMIN_HTML, css=ADMIN_CSS, testers=testers, count=count)

    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if hmac.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["admin_authenticated"] = True
            return redirect("/admin")
        error = "Mot de passe incorrect."

    return render_template_string(LOGIN_HTML, css=ADMIN_CSS, error=error)


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin")


@app.get("/admin/export.csv")
def admin_export():
    if not ADMIN_PASSWORD:
        return "ADMIN_PASSWORD n'est pas configuré sur le serveur.", 503
    if not admin_logged_in():
        return redirect("/admin")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "email", "created_at"])

    with Session(engine) as db:
        testers = db.scalars(select(Tester).order_by(Tester.id.asc())).all()
        for tester in testers:
            writer.writerow([tester.id, tester.email, tester.created_at.isoformat()])

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=spingo-testers.csv"},
    )


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
