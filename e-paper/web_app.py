from flask import Flask, render_template, jsonify
from data_logger import get_readings, init_db
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_data.db")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/readings")
def api_readings():
    days = int(os.environ.get("DAYS", "2"))
    readings = get_readings(days=days)
    return jsonify(readings)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
