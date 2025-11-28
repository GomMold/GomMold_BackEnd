from flask import Blueprint, jsonify, request
from openai import OpenAI
import os

chatbot_bp = Blueprint("chatbot_bp", __name__)

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY is missing")
    return OpenAI(api_key=api_key)

@chatbot_bp.route("/start", methods=["GET"])
def start_chat():
    return jsonify({
        "success": True,
        "data": {
            "message": "Hi! I'm Gom, your mold assistant. I can help you understand mold risks, prevention, and cleaning tips!"
        },
        "suggested_questions": [
            "How can I prevent mold from growing?",
            "What should I do if I see black mold?",
            "Is it safe to clean mold myself?"
        ]
    }), 200


@chatbot_bp.route("/query", methods=["POST"])
def query_chat():
    client = get_openai_client()

    body = request.json or {}
    question = body.get("question")

    if not question:
        return jsonify({"success": False, "error": "Missing question"}), 400

    try:
        # NEW OpenAI SDK (Responses API)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=question,
            instructions=(
                "You are a friendly mold-prevention assistant. "
                "Provide short, safe, and helpful advice."
            )
        )

        # Extract text properly (new SDK)
        answer = response.output_text

        return jsonify({"success": True, "data": {"answer": answer}}), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Chat service error",
            "details": str(e)
        }), 500
