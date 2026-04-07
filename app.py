from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "OK WORKING"

@app.route('/test')
def test():
    return "TEST OK"

import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
