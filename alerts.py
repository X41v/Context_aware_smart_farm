from state import alerts, latest_readings, actuators

alert_rules = [
    {"sensor": "ESP32_Soil", "condition": lambda v: v < 45, "message": "⚠ Soil moisture is too low! Consider irrigation."},
    {"sensor": "ESP32_TankLevel", "condition": lambda v: v < 30, "message": "⚠ Water tank is low! Refill soon."},
    {"sensor": "ESP32_pH", "condition": lambda v: v < 6 or v > 7.5, "message": "⚠ AB solution pH out of optimal range (6–7.5). Adjust nutrients."},
    {"sensor": "ESP32_Temp", "condition": lambda v: v < 15 or v > 35, "message": "⚠ Air temperature out of optimal range (15–35°C)."},
    {"sensor": "ESP32_Humidity", "condition": lambda v: v < 30 or v > 95, "message": "⚠ Air humidity out of optimal range (30–95%)."},
    {"sensor": "ESP32_Light", "condition": lambda v: v < 20, "message": "⚠ Light intensity is too low! Provide additional lighting."},
    {"sensor": "ESP32_WaterFlow", "condition": lambda v: actuators["Pump"] and v == 0, "message": "⚠ Pump is ON but no water flow detected! Check pipe or pump."},
    {"sensor": "ESP32_Gas", "condition": lambda v: v == "POOR", "message": "⚠ Gas quality is poor! Ventilate the area."}
]

def evaluate_alerts(readings):
    for rule in alert_rules:
        try:
            if rule["condition"](readings.get(rule["sensor"], 0)):
                alerts.append(rule["message"])
        except Exception as e:
            print(f"⚠ Alert error for {rule['sensor']}: {e}")
