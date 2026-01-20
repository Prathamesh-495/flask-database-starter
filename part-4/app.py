from flask import Flask, request, jsonify, render_template
from models import db, Book

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# GET Books (Pagination + Sorting)
@app.route("/api/books", methods=["GET"])
def get_books():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    allowed_sort = {
        "id": Book.id,
        "title": Book.title,
        "author": Book.author,
        "year": Book.year
    }

    sort_column = allowed_sort.get(sort, Book.id)
    sort_column = sort_column.desc() if order == "desc" else sort_column.asc()

    pagination = Book.query.order_by(sort_column).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total,
        "books": [
            {"id": b.id, "title": b.title, "author": b.author, "year": b.year}
            for b in pagination.items
        ]
    })


# POST Add Book
@app.route("/api/books", methods=["POST"])
def add_book():
    data = request.json

    book = Book(
        title=data.get("title"),
        author=data.get("author"),
        year=data.get("year")
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({"message": "Book added"}), 201


# PUT Edit Book
@app.route("/api/books/<int:id>", methods=["PUT"])
def edit_book(id):
    book = Book.query.get_or_404(id)
    data = request.json

    book.title = data.get("title", book.title)
    book.author = data.get("author", book.author)
    book.year = data.get("year", book.year)

    db.session.commit()
    return jsonify({"message": "Book updated"})


# DELETE Book
@app.route("/api/books/<int:id>", methods=["DELETE"])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"})


if __name__ == "__main__":
    app.run(debug=True)
