from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess
import os

# ==============================
# Flask app
# ==============================
app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "smart_farm.db"
RAG_DIR = BASE_DIR / "rag"
RAG_SCRIPT = RAG_DIR / "process_pdfs.py"

# ==============================
# Blueprints
# ==============================
from sensors import sensor_bp
from actuators import actuator_bp
from ai import ai_bp
from weather import weather_bp
from analytics import analytics_bp

app.register_blueprint(sensor_bp)
app.register_blueprint(actuator_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(analytics_bp)

# ==============================
# Shared state
# ==============================
from state import sensor_names, pump_schedules, alerts, latest_readings, actuators, manual_overrides, load_actuators_from_db

# Load actuators from DB on startup
load_actuators_from_db()

# ==============================
# PUMP SCHEDULE ROUTES
# ==============================
@app.route("/get-pump-schedule")
def get_pump_schedule():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, day, start_time, duration, on_duration, off_duration, type, enabled
        FROM pump_schedules
    """)
    rows = cursor.fetchall()
    conn.close()

    schedules = [
        {
            "id": r[0], "day": r[1], "start_time": r[2], "duration": r[3],
            "on_duration": r[4], "off_duration": r[5], "type": r[6], "enabled": bool(r[7])
        } for r in rows
    ]

    pump_schedules[:] = schedules
    return jsonify(schedules)

@app.route("/set-pump-schedule", methods=["POST"])
def set_pump_schedule():
    data = request.json
    schedule_type = data.get("type", "single")
    day = data.get("day")
    start_time = data.get("start_time")
    duration = int(data.get("duration", 0))
    on_duration = int(data.get("on_duration", 0))
    off_duration = int(data.get("off_duration", 0))

    # Use default start_time for cycle schedule
    if schedule_type == "cycle":
        start_time = "00:00"

    # Validation
    if schedule_type == "single" and (not start_time or duration <= 0):
        return jsonify({"success": False, "error": "Provide valid start_time and duration for single schedule."})
    if schedule_type == "cycle" and (on_duration <= 0 or off_duration <= 0):
        return jsonify({"success": False, "error": "Provide valid on/off durations for cycle schedule."})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Remove duplicate schedule for same day+time+type
    cursor.execute(
        "DELETE FROM pump_schedules WHERE day=? AND start_time=? AND type=?",
        (day, start_time, schedule_type)
    )

    # Insert new schedule
    cursor.execute("""
        INSERT INTO pump_schedules(day, start_time, duration, on_duration, off_duration, type, enabled)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (day, start_time, duration, on_duration, off_duration, schedule_type))

    conn.commit()
    conn.close()
    return get_pump_schedule()

@app.route("/delete-pump-schedule", methods=["POST"])
def delete_pump_schedule():
    schedule_id = request.json.get("id")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pump_schedules WHERE id=?", (schedule_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# ==============================
# Scheduler thread
# ==============================
from pump_scheduler import start_scheduler_thread
start_scheduler_thread()

# ==============================
# DASHBOARD ROUTES
# ==============================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/settings")
def settings():
    return render_template(
        "settings.html",
        sensor_names=sensor_names,
        schedules=pump_schedules
    )

@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/latest-data")
def get_latest_data():
    return jsonify({
        "readings": latest_readings,
        "alerts": alerts
    })

# ==============================
# AI FILE MANAGEMENT & RETRAIN
# ==============================
DATA_PATH = BASE_DIR / "data"

@app.route("/files", methods=["GET"])
def list_files():
    files = [f for f in os.listdir(DATA_PATH) if f.lower().endswith(".pdf")]
    return jsonify({"files": files})

@app.route("/files/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided"})
    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "error": "Only PDF files allowed"})
    file_path = DATA_PATH / file.filename
    file.save(file_path)
    return jsonify({"success": True, "filename": file.filename})

@app.route("/files/delete", methods=["POST"])
def delete_file():
    data = request.json
    filename = data.get("filename")
    if not filename or not filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "error": "Invalid file"})
    file_path = DATA_PATH / filename
    if file_path.exists():
        os.remove(file_path)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "File not found"})

@app.route("/files/view/<filename>")
def view_file(filename):
    return send_from_directory(DATA_PATH, filename)

@app.route("/retrain-ai", methods=["POST"])
def retrain_ai():
    try:
        # Run process_pdfs.py with absolute path and correct working directory
        subprocess.run(["python3", str(RAG_SCRIPT.resolve())], check=True, cwd=str(RAG_DIR))
        return jsonify({"success": True, "message": "AI retraining complete"})
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": str(e)})

# ==============================
# RUN SERVER
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
