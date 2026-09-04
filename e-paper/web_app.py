from flask import Flask, render_template, jsonify, request
from data_logger import get_readings, get_daily_aggregates, init_db
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weather_data.db")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/readings")
def api_readings():
    # allow ?days= override, fallback to env DAYS or 2
    qdays = request.args.get("days")
    if qdays is not None:
        try:
            days = int(qdays)
        except ValueError:
            days = int(os.environ.get("DAYS", "2"))
    else:
        days = int(os.environ.get("DAYS", "2"))
    readings = get_readings(days=days)
    return jsonify(readings)


@app.route("/api/yearly")
def api_yearly():
    """Daily aggregates for the last year (default 365 days).

    Query param: ?days=365
    Returns: [{day, internal_avg/min/max, external_avg/min/max, ...}, ...]
    """
    try:
        days = int(request.args.get("days", "365"))
    except ValueError:
        days = 365
    # clamp to reasonable range
    days = max(7, min(days, 730))
    data = get_daily_aggregates(days=days)
    return jsonify(data)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
