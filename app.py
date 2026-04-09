from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
import os

app = Flask(__name__)
CORS(app)

# Подключение к БД
db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)

@app.route('/')
def home():
    return "API работает"

import hashlib

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').lower()
        password = data.get('password', '')

        cursor = db.cursor()
        cursor.execute("SELECT password, salt FROM authme WHERE username=%s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"status": "error", "msg": "user not found"})

        db_hash = user[0]
        salt = user[1]

        # Вариант 1
        hash1 = hashlib.sha256((password + salt).encode()).hexdigest()

        # Вариант 2
        hash2 = hashlib.sha256(
            (hashlib.sha256(password.encode()).hexdigest() + salt).encode()
        ).hexdigest()

        if hash1 == db_hash or hash2 == db_hash:
            return jsonify({"status": "ok"})

        return jsonify({"status": "error", "msg": "wrong password"})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})
# запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
