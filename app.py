from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import hashlib
import os

app = Flask(__name__)
CORS(app)

# 🔗 Подключение к БД
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

        db_hash_full = user[0]

        # 🔥 парсим строку $SHA$salt$hash
        if db_hash_full.startswith("$SHA$"):
            parts = db_hash_full.split("$")
            salt = parts[2]
            db_hash = parts[3]

            # SHA256(SHA256(password) + salt)
            first = hashlib.sha256(password.encode()).hexdigest()
            final = hashlib.sha256((first + salt).encode()).hexdigest()

            if final == db_hash:
                return jsonify({"status": "ok"})

        return jsonify({"status": "error", "msg": "wrong password"})

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)})
        
@app.route("/profile", methods=["POST"])
def profile():
    username = request.json["username"]

    cursor = db.cursor(pymysql.cursors.DictCursor)

    # 1. ищем игрока
    cursor.execute(
        "SELECT * FROM user_data WHERE username=%s",
        (username,)
    )
    user = cursor.fetchone()

    # 2. если нет — создаём
    if not user:
        cursor.execute(
            "INSERT INTO user_data (username, balance, role, skin) VALUES (%s, 0, 'player', NULL)",
            (username,)
        )
        db.commit()

        return {
            "username": username,
            "balance": 0,
            "role": "player",
            "skin": None
        }

    # 3. если есть — возвращаем
    return {
        "username": user["username"],
        "balance": user["balance"],
        "role": user["role"],
        "skin": user["skin"]
    }
# 🚀 запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
