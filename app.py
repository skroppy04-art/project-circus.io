from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import bcrypt
import os
import hashlib
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

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').lower()
        password = data.get('password', '')

        cursor = db.cursor()
        cursor.execute(
            "SELECT password FROM authme WHERE LOWER(username)=%s OR LOWER(realname)=%s",
            (username, username)
        )
        user = cursor.fetchone()

        if not user:
            return jsonify({"status": "error", "msg": "user not found"})

        db_hash = user[0]

        # 2 варианта (lower + upper)
        hash_lower = hashlib.sha256(password.encode()).hexdigest()
        hash_upper = hash_lower.upper()

        if db_hash == hash_lower or db_hash == hash_upper:
            return jsonify({"status": "ok"})

        return jsonify({"status": "error", "msg": "wrong password"})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})
# запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
