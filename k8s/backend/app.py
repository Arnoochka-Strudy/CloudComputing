from flask import Flask, jsonify, Response
app = Flask(__name__)

@app.route("/")
def index() -> Response:
    return jsonify({"message": "OK"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
