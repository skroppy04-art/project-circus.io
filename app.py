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

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').lower()
    password = data.get('password', '')

    cursor = db.cursor()
    cursor.execute("SELECT password FROM authme WHERE username=%s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode(), user[0].encode()):
        return jsonify({"status": "ok"})
    
    return jsonify({"status": "error"})

# запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
