import time
from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime
from services.groq_client import call_groq
from utils.metrics import start_time, response_times

ai_bp = Blueprint("ai", __name__)

# =========================
# 🔹 DESCRIBE ENDPOINT
# =========================
@ai_bp.route("/describe", methods=["POST"])
def describe():
    data = request.get_json()

    # 🔒 INPUT VALIDATION
    if not data or "input" not in data:
        return jsonify({"error": "Missing 'input' field"}), 400

    user_input = data["input"].strip()

    if len(user_input) == 0:
        return jsonify({"error": "Input cannot be empty"}), 400

    # 📄 LOAD PROMPT
    prompt_path = os.path.join("prompts", "describe_prompt.txt")

    try:
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    except Exception:
        return jsonify({"error": "Prompt file not found"}), 500

    prompt = prompt_template.replace("{user_input}", user_input)

    # 🤖 CALL GROQ
    response = call_groq(prompt)

    # 🚨 FALLBACK (Day 9)
    if not response:
        return jsonify({
            "severity": "UNKNOWN",
            "summary": "AI service unavailable",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat()
        })

    try:
        result = json.loads(response)
    except:
        return jsonify({
            "severity": "UNKNOWN",
            "summary": "Invalid AI response",
            "is_fallback": True
        })

    # 🕒 ADD TIMESTAMP
    result["generated_at"] = datetime.utcnow().isoformat()

    return jsonify(result)


# =========================
# 🔹 GENERATE REPORT
# =========================
@ai_bp.route("/generate-report", methods=["POST"])
def generate_report():
    data = request.get_json()

    # 🔒 INPUT VALIDATION
    if not data or "input" not in data:
        return jsonify({"error": "Missing input"}), 400

    user_input = data["input"].strip()

    if len(user_input) == 0:
        return jsonify({"error": "Input cannot be empty"}), 400

    # 📄 LOAD PROMPT
    prompt_path = os.path.join("prompts", "report_prompt.txt")

    try:
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    except Exception:
        return jsonify({"error": "Prompt file not found"}), 500

    prompt = prompt_template.replace("{input}", user_input)

    # 🤖 CALL GROQ
    response = call_groq(prompt)

    # 🚨 FALLBACK (Day 9)
    if not response:
        return jsonify({
            "title": "Fallback Report",
            "summary": "AI service unavailable",
            "overview": "Unable to generate report",
            "key_items": [],
            "recommendations": [],
            "is_fallback": True
        })

    try:
        return jsonify(json.loads(response))
    except:
        return jsonify({
            "error": "Invalid JSON from AI",
            "is_fallback": True
        })


# =========================
# 🔹 HEALTH ENDPOINT
# =========================
@ai_bp.route("/health", methods=["GET"])
def health():
    uptime = time.time() - start_time

    avg_time = 0
    if response_times:
        avg_time = sum(response_times) / len(response_times)

    return jsonify({
        "status": "UP",
        "model": "groq-llama",
        "avg_response_time_ms": round(avg_time, 2),
        "uptime_seconds": int(uptime)
    })