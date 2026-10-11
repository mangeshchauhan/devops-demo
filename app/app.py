from flask import Flask, jsonify
import os

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "v1")

@app.route("/")
def home():
    return f"<h1>Hello from CI/CD pipeline!🚀</h1><p>Version: {VERSION}</p>"

@app.route("/health")
def health():
    return jsonify(status="ok")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
