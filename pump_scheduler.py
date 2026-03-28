import threading
import time
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "smart_farm.db"

from state import actuators, manual_overrides

def get_active_schedules():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT day, start_time, duration, on_duration, off_duration, type
        FROM pump_schedules WHERE enabled=1
    """)
    rows = cursor.fetchall()
    conn.close()
    schedules = [
        {
            "day": r[0],
            "start_time": r[1],
            "duration": r[2],
            "on_duration": r[3],
            "off_duration": r[4],
            "type": r[5]
        } for r in rows
    ]
    return schedules

def pump_scheduler_loop():
    last_active_schedule = None
    while True:
        now = datetime.now()
        current_day = now.strftime("%A")
        current_time = now.time()

        schedules = get_active_schedules()
        active_schedule = None

        for sched in schedules:
            if sched["day"] == current_day or sched["day"].lower() == "all":
                start_dt = datetime.strptime(sched["start_time"], "%H:%M")
                if sched["type"] == "single":
                    end_dt = start_dt + timedelta(minutes=int(sched["duration"]))
                    if start_dt.time() <= current_time < end_dt.time():
                        active_schedule = sched
                        break
                elif sched["type"] == "cycle":
                    # elapsed minutes since start
                    elapsed = (now - start_dt).total_seconds() // 60
                    cycle_len = sched["on_duration"] + sched["off_duration"]
                    if elapsed >= 0:
                        cycle_pos = elapsed % cycle_len
                        if cycle_pos < sched["on_duration"]:
                            active_schedule = sched
                            break

        if active_schedule != last_active_schedule:
            manual_overrides["Pump"] = None
            last_active_schedule = active_schedule

        if active_schedule:
            if manual_overrides["Pump"] is None:
                actuators["Pump"] = True
        else:
            if manual_overrides["Pump"] is None:
                actuators["Pump"] = False

        time.sleep(10)

def start_scheduler_thread():
    threading.Thread(target=pump_scheduler_loop, daemon=True).start()
