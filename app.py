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
    database=os.getenv("DB_NAME"),
    cursorclass=pymysql.cursors.Cursor
)

# 🟢 Проверка сервера
@app.route('/')
def home():
    return "API работает"

# 🔐 ЛОГИН
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

        # 🔍 считаем хэш
        input_hash = hashlib.sha256(password.encode()).hexdigest()

        # 🔥 DEBUG (смотри в Render Logs)
        print("DB HASH:", db_hash)
        print("INPUT HASH:", input_hash)

        # ✅ проверка (с учётом регистра)
        if db_hash.lower() == input_hash.lower():
            return jsonify({"status": "ok"})

        return jsonify({"status": "error", "msg": "wrong password"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error", "msg": str(e)})

# 🚀 запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
