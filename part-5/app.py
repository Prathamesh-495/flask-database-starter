import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///default.db")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Connection pooling (production ready)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_size": 10,
    "pool_recycle": 3600,
    "pool_pre_ping": True,
}

db = SQLAlchemy(app)

# =========================
# MODEL
# =========================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

# =========================
# ROUTES
# =========================
@app.route("/")
def index():
    products = Product.query.all()

    db_type = "Unknown"
    db_url = DATABASE_URL.lower()
    if "postgres" in db_url:
        db_type = "PostgreSQL"
    elif "mysql" in db_url:
        db_type = "MySQL"
    elif "sqlite" in db_url:
        db_type = "SQLite"

    return render_template(
        "index.html",
        products=products,
        db_type=db_type,
        db_url=DATABASE_URL,
    )

@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        product = Product(
            name=request.form["name"],
            price=float(request.form["price"]),
            stock=int(request.form.get("stock", 0)),
            description=request.form.get("description", ""),
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/delete/<int:id>")
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted!", "danger")
    return redirect(url_for("index"))

# =========================
# DATABASE INITIALIZATION
# =========================
def init_db():
    try:
        with app.app_context():
            db.create_all()
            print(f"✅ Connected to database: {DATABASE_URL}")

            if Product.query.count() == 0:
                db.session.add_all([
                    Product(name="Laptop", price=999.99, stock=10),
                    Product(name="Mouse", price=29.99, stock=50),
                    Product(name="Keyboard", price=79.99, stock=30),
                ])
                db.session.commit()
                print("✅ Sample data inserted")

    except OperationalError as e:
        print("❌ DATABASE CONNECTION FAILED")
        print("Reason:", e)
        print("Check DATABASE_URL, username, password, host, and port.")
        exit(1)

# =========================
# APP START
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True")
