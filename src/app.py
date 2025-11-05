import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS')

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)

# Initialize Firebase
try:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase connected!")
except Exception as e:
    print(f"Firebase error: {e}")
    db = None

# JWT Helper Functions
def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# Routes
@app.route('/health', methods=['GET'])
def health():
    return {'status': 'healthy', 'firebase': db is not None}, 200

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    if db is None:
        return jsonify({'error': 'Database not available'}), 500
    
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    username = data.get('username') or ''

    if not email or not password or not username:
        return jsonify({'error': 'Missing fields'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password too short'}), 400

    users_ref = db.collection('users')
    if users_ref.where('email', '==', email).get():
        return jsonify({'error': 'Email already exists'}), 400

    hashed = generate_password_hash(password)
    doc_ref = users_ref.add({
        'email': email,
        'password': hashed,
        'username': username,
        'created_at': datetime.datetime.utcnow()
    })
    token = create_token(doc_ref[1].id)
    return jsonify({'success': True, 'token': token, 'user': {'id': doc_ref[1].id, 'email': email, 'username': username}}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():

    if db is None:
        return jsonify({'error': 'Database not available'}), 500
   
    data = request.json or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    users_ref = db.collection('users')
    users = list(users_ref.where('email', '==', email).get())
    if not users:
        return jsonify({'error': 'Invalid email or password'}), 401

    user_doc = users[0]
    user_data = user_doc.to_dict()
    if not check_password_hash(user_data['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_token(user_doc.id)
    return jsonify({'success': True, 'token': token, 'user': {'id': user_doc.id, 'email': email, 'username': user_data['username']}}), 200

@app.route('/api/user/profile', methods=['GET'])
@token_required
def profile(current_user_id):

    if db is None:
        return jsonify({'error': 'Database not available'}), 500
    
    doc = db.collection('users').document(current_user_id).get()
  
    if not doc.exists:
        return jsonify({'error': 'User not found'}), 404
    
    user = doc.to_dict()
    return jsonify({'id': current_user_id, 'email': user.get('email'), 'username': user.get('username')}), 200

# Start Server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)