from flask import Blueprint, request, jsonify
from state import actuators, manual_overrides, update_actuator_db

actuator_bp = Blueprint("actuators", __name__)

# ==============================
# Get current actuator states
# ==============================
@actuator_bp.route("/actuators")
def get_actuators():
    return jsonify(actuators)

# ==============================
# Toggle actuator from dashboard
# ==============================
@actuator_bp.route("/toggle-actuator", methods=["POST"])
def toggle_actuator():
    data = request.json
    name = data.get("name")
    state = data.get("state")
    
    if name in actuators:
        actuators[name] = state
        manual_overrides[name] = state  # keep manual override
        update_actuator_db(name, state)  # save to DB
        return jsonify({"success": True})
    
    return jsonify({"success": False})
