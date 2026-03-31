import sqlite3
from pathlib import Path

# ==============================
# Shared state
# ==============================
sensor_names = [
    "ESP32_Temp", "ESP32_Humidity", "ESP32_Pressure", "ESP32_Light", "ESP32_Rain",
    "ESP32_Soil", "ESP32_SoilTemp", "ESP32_Gas", "ESP32_WaterFlow", "ESP32_TankLevel",
    "ESP32_pH", "ESP32_TDS"
]
latest_readings = {name: 0 for name in sensor_names}

alerts = []

actuators = {"Fan": False, "Light": False, "Pump": False}
manual_overrides = {"Pump": None}

pump_schedules = []  # memory copy for dashboard and scheduler

# ==============================
# DB path
# ==============================
DB_PATH = Path(__file__).resolve().parent / "smart_farm.db"

# ==============================
# Load actuators from DB on startup
# ==============================
def load_actuators_from_db():
    global actuators
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, state FROM actuators")
        rows = cursor.fetchall()
        conn.close()
        for name, state in rows:
            actuators[name] = bool(state)
        print("✅ Loaded actuators from DB:", actuators)
    except Exception as e:
        print("⚠ Failed to load actuators from DB:", e)

# ==============================
# Update actuator in DB
# ==============================
def update_actuator_db(name, state):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Insert or replace current state
        cursor.execute(
            "INSERT INTO actuators(name, state) VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET state=excluded.state",
            (name, int(state))
        )
        conn.commit()
        conn.close()
        print(f"✅ Actuator '{name}' state saved to DB: {state}")
    except Exception as e:
        print(f"⚠ Failed to update actuator '{name}' in DB:", e)
