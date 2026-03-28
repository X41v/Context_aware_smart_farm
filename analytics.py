from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime, timedelta

analytics_bp = Blueprint("analytics", __name__)

DB_PATH = "smart_farm.db"

@analytics_bp.route("/analytics-data")
def analytics_data():
    # Get range parameter
    time_range = request.args.get("range", "day")

    now = datetime.now()
    if time_range == "hour":
        since = now - timedelta(hours=1)
        interval = timedelta(minutes=5)
    elif time_range == "day":
        since = now - timedelta(days=1)
        interval = timedelta(minutes=15)
    elif time_range == "week":
        since = now - timedelta(weeks=1)
        interval = timedelta(hours=1)
    elif time_range == "month":
        since = now - timedelta(days=30)
        interval = timedelta(days=1)
    else:
        since = now - timedelta(days=1)
        interval = timedelta(minutes=15)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sensor_name, value, timestamp
        FROM sensor_data
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
    """, (since.isoformat(),))

    rows = cursor.fetchall()
    conn.close()

    data = {}
    for sensor, value, ts in rows:
        ts_dt = datetime.fromisoformat(ts)

        # Round timestamp to nearest interval
        total_seconds = (ts_dt - datetime(1970,1,1)).total_seconds()
        interval_seconds = interval.total_seconds()
        rounded_seconds = (total_seconds // interval_seconds) * interval_seconds
        ts_interval = datetime.utcfromtimestamp(rounded_seconds)

        if sensor not in data:
            data[sensor] = {}

        if ts_interval not in data[sensor]:
            data[sensor][ts_interval] = {"sum": 0, "count": 0}

        data[sensor][ts_interval]["sum"] += float(value)
        data[sensor][ts_interval]["count"] += 1

    # Prepare final JSON
    result = {}
    for sensor, intervals in data.items():
        result[sensor] = {"labels": [], "values": []}
        for ts_interval in sorted(intervals):
            avg_value = intervals[ts_interval]["sum"] / intervals[ts_interval]["count"]

            # Clamp values
            if sensor in ["ESP32_Rain", "ESP32_Soil", "ESP32_TankLevel"]:
                avg_value = max(0, min(100, avg_value))
            elif sensor == "ESP32_pH":
                avg_value = max(0, min(14, avg_value))

            result[sensor]["labels"].append(ts_interval.isoformat())
            result[sensor]["values"].append(round(avg_value, 2))

    return jsonify(result)
