# Run this command to install required modules:
# pip install flask flask-pymongo flask-bcrypt python-dotenv pyjwt

from flask import Flask, request, jsonify, make_response
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/bookstore")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret-key-for-dev")

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)

# Collections
users_collection = mongo.db.users
books_collection = mongo.db.books

# Helper Functions
def generate_token(user_id):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = users_collection.find_one({'_id': ObjectId(data['user_id'])})
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated

def admin_required(f):
    """Decorator to verify admin role"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.get('is_admin', False):
            return jsonify({'message': 'Admin access required!'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# Routes
@app.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required!'}), 400
    
    # Check if user already exists
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists!'}), 400
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    
    # Create new user
    user = {
        'email': data['email'],
        'password': hashed_password,
        'name': data.get('name', ''),
        'is_admin': data.get('is_admin', False),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Insert user into database
    user_id = users_collection.insert_one(user).inserted_id
    
    # Generate token
    token = generate_token(user_id)
    
    return jsonify({
        'message': 'User registered successfully!',
        'token': token,
        'user_id': str(user_id)
    }), 201

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required!'}), 400
    
    # Find user
    user = users_collection.find_one({'email': data['email']})
    
    if not user or not bcrypt.check_password_hash(user['password'], data['password']):
        return jsonify({'message': 'Invalid credentials!'}), 401
    
    # Generate token
    token = generate_token(user['_id'])
    
    return jsonify({
        'message': 'Logged in successfully!',
        'token': token,
        'user_id': str(user['_id'])
    }), 200

@app.route('/books', methods=['GET'])
def get_books():
    """Get all books (public endpoint)"""
    books = []
    for book in books_collection.find():
        book['_id'] = str(book['_id'])
        books.append(book)
    
    return jsonify({'books': books}), 200

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """Get a single book by ID (public endpoint)"""
    try:
        book = books_collection.find_one({'_id': ObjectId(book_id)})
        
        if not book:
            return jsonify({'message': 'Book not found!'}), 404
            
        book['_id'] = str(book['_id'])
        return jsonify(book), 200
        
    except:
        return jsonify({'message': 'Invalid book ID!'}), 400

@app.route('/books', methods=['POST'])
@token_required
def add_book(current_user):
    """Add a new book (authenticated endpoint)"""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({'message': 'Title and author are required!'}), 400
    
    # Create book document
    book = {
        'title': data['title'],
        'author': data['author'],
        'description': data.get('description', ''),
        'published_year': data.get('published_year'),
        'created_by': str(current_user['_id']),
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }
    
    # Insert book into database
    book_id = books_collection.insert_one(book).inserted_id
    
    return jsonify({
        'message': 'Book added successfully!',
        'book_id': str(book_id)
    }), 201

@app.route('/books/<book_id>', methods=['PUT'])
@token_required
def update_book(current_user, book_id):
    """Update a book (authenticated endpoint)"""
    data = request.get_json()
    
    try:
        # Find the book
        book = books_collection.find_one({'_id': ObjectId(book_id)})
        
        if not book:
            return jsonify({'message': 'Book not found!'}), 404
            
        # Check if user is the creator or admin
        if str(book['created_by']) != str(current_user['_id']) and not current_user.get('is_admin', False):
            return jsonify({'message': 'Not authorized to update this book!'}), 403
        
        # Update book data
        update_data = {
            'title': data.get('title', book['title']),
            'author': data.get('author', book['author']),
            'description': data.get('description', book.get('description', '')),
            'published_year': data.get('published_year', book.get('published_year')),
            'updated_at': datetime.utcnow()
        }
        
        # Update in database
        books_collection.update_one(
            {'_id': ObjectId(book_id)},
            {'$set': update_data}
        )
        
        return jsonify({'message': 'Book updated successfully!'}), 200
        
    except:
        return jsonify({'message': 'Invalid book ID!'}), 400

@app.route('/books/<book_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_book(current_user, book_id):
    """Delete a book (admin only endpoint)"""
    try:
        result = books_collection.delete_one({'_id': ObjectId(book_id)})
        
        if result.deleted_count == 0:
            return jsonify({'message': 'Book not found!'}), 404
            
        return jsonify({'message': 'Book deleted successfully!'}), 200
        
    except:
        return jsonify({'message': 'Invalid book ID!'}), 400

# Error Handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found!'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error!'}), 500

if __name__ == '__main__':
    app.run(debug=True)




    