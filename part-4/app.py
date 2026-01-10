from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# ---------------- DATABASE ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'api_demo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- MODEL ----------------
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year
        }

# ---------------- FRONTEND ----------------
@app.route('/')
def home():
    return render_template("index.html")

# ---------------- API ----------------

# ✅ GET /api/books?page=1&per_page=10&sort=title&order=desc
@app.route('/api/books', methods=['GET'])
def get_books():
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Sorting
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    allowed_sort = {
        "id": Book.id,
        "title": Book.title,
        "author": Book.author,
        "year": Book.year
    }

    sort_column = allowed_sort.get(sort, Book.id)
    sort_column = sort_column.desc() if order == "desc" else sort_column.asc()

    pagination = Book.query.order_by(sort_column).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "success": True,
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "books": [book.to_dict() for book in pagination.items]
    })

# ---------------- INIT DB ----------------
def init_db():
    with app.app_context():
        db.create_all()
        if Book.query.count() == 0:
            db.session.add_all([
                Book(title="Python Crash Course", author="Eric Matthes", year=2019),
                Book(title="Flask Web Development", author="Miguel Grinberg", year=2018),
                Book(title="Clean Code", author="Robert C. Martin", year=2008),
                Book(title="Effective Python", author="Brett Slatkin", year=2020),
                Book(title="Design Patterns", author="Erich Gamma", year=1994),
            ])
            db.session.commit()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
