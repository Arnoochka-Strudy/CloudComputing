import requests
from flask import Flask

app = Flask(__name__)

BACKEND_URL = "http://backend:5000/"

@app.route("/")
def index() -> str:
    try:
        resp = requests.get(BACKEND_URL).json()
        return f"Frontend: OK<br>Backend: {resp['message']}"
    except Exception as e:
        return f"Frontend: OK<br>Backend: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)