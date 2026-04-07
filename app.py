from flask import Flask, request, jsonify
import pymysql
import bcrypt
import os

app = Flask(__name__)

db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username'].lower()
    password = data['password']

    cursor = db.cursor()
    cursor.execute("SELECT password FROM authme WHERE username=%s", (username,))
    user = cursor.fetchone()

    if user and bcrypt.checkpw(password.encode(), user[0].encode()):
        return jsonify({"status": "ok"})
    
    return jsonify({"status": "error"})

app.run(host="0.0.0.0", port=10000)
