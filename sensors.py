from flask import Blueprint, request, jsonify
from state import latest_readings, alerts, sensor_names
from alerts import evaluate_alerts
import sqlite3
from pathlib import Path
import threading
import time
from datetime import datetime, timedelta

sensor_bp = Blueprint("sensors", __name__)

# Database path
DB_PATH = Path(__file__).resolve().parent / "smart_farm.db"

# Track last time sensor sent data
sensor_last_seen = {}

# Helper: save sensor reading to DB
def save_sensor_data(node_id, sensor_name, value):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sensor_data(node_id, sensor_name, value) VALUES (?, ?, ?)",
            (node_id, sensor_name, value)
        )
        conn.commit()
    except Exception as e:
        print(f"⚠ Failed to save sensor data: {e}")
    finally:
        conn.close()


@sensor_bp.route("/sensor-data", methods=["POST"])
def receive_sensor_data():
    data = request.json
    node_id = data.get("node_id")
    if not node_id:
        return jsonify({"error": "Missing node_id"}), 400

    print(f"📡 Data from {node_id}: {data}")

    # Map ESP32 keys to internal sensor names
    mapping = {
        "soil_moisture": "ESP32_Soil",
        "temperature": "ESP32_Temp",
        "humidity": "ESP32_Humidity",
        "pressure": "ESP32_Pressure",
        "light": "ESP32_Light",
        "rain": "ESP32_Rain",
        "soil_temp": "ESP32_SoilTemp",
        "gas": "ESP32_Gas",
        "water_flow": "ESP32_WaterFlow",
        "tank_level": "ESP32_TankLevel",
        "ph": "ESP32_pH",
        "tds": "ESP32_TDS",
       
    }

    now = datetime.now()

    # Update in-memory state and save to DB
    for key, sensor in mapping.items():
        if key in data:
            latest_readings[sensor] = data[key]
            sensor_last_seen[sensor] = now
            save_sensor_data(node_id, sensor, data[key])

    # Evaluate alerts (still in-memory for now)
    alerts.clear()
    evaluate_alerts(latest_readings)

    return jsonify({"status": "success"})


# -------------------- OFFLINE DETECTOR --------------------
def mark_sensors_offline():
    while True:
        now = datetime.now()

        for sensor, last_time in list(sensor_last_seen.items()):
            if now - last_time > timedelta(seconds=90):
                latest_readings[sensor] = "Offline"

        time.sleep(5)


# Start background thread
threading.Thread(target=mark_sensors_offline, daemon=True).start()
