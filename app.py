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

async function login() {
    const username = document.getElementById("login").value;
    const password = document.getElementById("password").value;

    const status = document.getElementById("loginStatus");
    status.innerText = "Загрузка...";

    try {
        const res = await fetch("https://project-circus-io.onrender.com/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await res.json();

        // 🔥 ВАЖНО: показываем ВСЁ что пришло
        status.innerText = JSON.stringify(data);

    } catch (e) {
        status.innerText = "Ошибка: " + e;
    }
}

# 🚀 запуск
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
