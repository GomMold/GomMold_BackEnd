from flask import Blueprint, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

chatbot_bp = Blueprint("chatbot_bp", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@chatbot_bp.route("/start", methods=["GET"])
def start_chat():
    greeting_message = {
        "success": True,
        "data": {
            "message": "Hi! I'm Gom, your mold assistant. I can help you understand mold risks, prevention, and cleaning tips!"
        },
        "suggested_questions": [
            "How can I prevent mold from growing?",
            "What should I do if I see black mold?",
            "Is it safe to clean mold myself?"
        ]
    }
    return jsonify(greeting_message), 200

@chatbot_bp.route("/query", methods=["POST"])
def query_chat():
    data = request.json or {}
    question = data.get("question")

    if not question:
        return jsonify({"success": False, "error": "Missing question"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly and informative mold prevention assistant. Provide short, clear, and safe advice about mold."},
                {"role": "user", "content": question}
            ],
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"success": True, "data": {"answer": answer}}), 200

    except Exception as e:
        return jsonify({"success": False, "error": "Chat service unavailable", "details": str(e)}), 500
