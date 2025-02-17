from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    borrowed_books = db.relationship('Borrow', backref='user', lazy=True)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    borrows = db.relationship('Borrow', backref='book', lazy=True)

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email} for u in users])

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get_or_404(user_id)
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify({'message': 'User updated'})

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

@app.route('/authors', methods=['POST'])
def add_author():
    data = request.get_json()
    author = Author(name=data['name'])
    db.session.add(author)
    db.session.commit()
    return jsonify({'message': 'New author added'})

@app.route('/authors', methods=['GET'])
def get_authors():
    authors = Author.query.all()
    return jsonify([{'id': a.id, 'name': a.name} for a in authors])

@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    book = Book(title=data['title'], author_id=data['author_id'])
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'New book added'})

@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{'id': b.id, 'title': b.title, 'author_id': b.author_id} for b in books])

@app.route('/books/author/<int:author_id>', methods=['GET'])
def get_books_by_author(author_id):
    books = Book.query.filter_by(author_id=author_id).all()
    return jsonify([{'id': b.id, 'title': b.title} for b in books])

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

@app.route('/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    borrow = Borrow(user_id=data['user_id'], book_id=data['book_id'])
    db.session.add(borrow)
    db.session.commit()
    return jsonify({'message': 'Book borrowed'})

@app.route('/borrow/user/<int:user_id>', methods=['GET'])
def get_borrowed_books(user_id):
    borrows = Borrow.query.filter_by(user_id=user_id).all()
    return jsonify([{'id': b.id, 'book_id': b.book_id, 'borrow_date': b.borrow_date} for b in borrows])

@app.route('/borrow/book/<int:book_id>', methods=['GET'])
def get_users_who_borrowed(book_id):
    borrows = Borrow.query.filter_by(book_id=book_id).all()
    return jsonify([{'id': b.id, 'user_id': b.user_id, 'borrow_date': b.borrow_date} for b in borrows])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
