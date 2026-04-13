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
    data = request.json
    username_input = data.get('username')
    password = data.get('password')

    cursor = db.cursor()

    cursor.execute(
        "SELECT realname, password FROM authme WHERE LOWER(realname)=%s",
        (username_input.lower(),)
    )

    user = cursor.fetchone()

    if not user:
        return {"status": "error"}

    realname = user[0]
    db_hash_full = user[1]

    # проверка пароля
    # ...

    username_lower = realname.lower()

    # 🔥 Проверяем по lowercase username
    cursor.execute(
        "SELECT * FROM user_data WHERE username=%s",
        (username_lower,)
    )
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(
            "INSERT INTO user_data (username, realname, balance, role) VALUES (%s, %s, 0, 'player')",
            (username_lower, realname)
        )
        db.commit()

    return {
        "status": "ok",
        "username": realname
    }
        
@app.route("/profile", methods=["POST"])
def profile():
    username = request.json.get("username")

    if not username:
        return {"error": "no username"}

    cursor = db.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM user_data WHERE username=%s", (username,))
    user = cursor.fetchone()

    return user if user else {"error": "not found"}
# 🚀 запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
