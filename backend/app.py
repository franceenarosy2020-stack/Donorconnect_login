from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from config import MONGO_URI, JWT_SECRET

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = MONGO_URI
app.config["SECRET_KEY"] = JWT_SECRET
mongo = PyMongo(app)

# Create geospatial index once at startup
with app.app_context():
    mongo.db.users.create_index([("location", "2dsphere")])


@app.route('/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        required = ['name', 'email', 'phone', 'password', 'city', 'blood_group', 'latitude', 'longitude']
        for field in required:
            if not data.get(field) and data.get(field) != 0:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        if mongo.db.users.find_one({"email": data['email']}):
            return jsonify({"error": "Email already registered"}), 400

        if mongo.db.users.find_one({"phone": data['phone']}):
            return jsonify({"error": "Phone number already registered"}), 400

        user_doc = {
            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],
            "password": generate_password_hash(data['password']),
            "city": data['city'],
            "blood_group": data['blood_group'],
            "location": {
                "type": "Point",
                "coordinates": [float(data['longitude']), float(data['latitude'])]
            },
            "role": "user",
            "is_donor": bool(data.get('is_donor', False)),
            "is_requester": bool(data.get('is_requester', False)),
            "created_at": datetime.datetime.utcnow()
        }

        result = mongo.db.users.insert_one(user_doc)

        if not result.inserted_id:
            return jsonify({"error": "Failed to create account. Please try again."}), 500

        return jsonify({"message": "Registration successful"}), 201

    except Exception as e:
        print(f"[REGISTER ERROR] {e}")
        return jsonify({"error": "Server error during registration."}), 500


@app.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400

        user = mongo.db.users.find_one({"email": data['email']})

        if not user or not check_password_hash(user['password'], data['password']):
            return jsonify({"error": "Invalid Email or Password"}), 401

        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config["SECRET_KEY"], algorithm="HS256")

        return jsonify({
            "token": token,
            "user": {
                "name": user['name'],
                "role": user['role'],
                "email": user['email'],
                "is_donor": user.get('is_donor', False),
                "is_requester": user.get('is_requester', False)
            }
        }), 200

    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return jsonify({"error": "Server error during login."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)