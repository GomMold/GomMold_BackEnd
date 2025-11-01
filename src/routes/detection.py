from flask import Blueprint, request, jsonify

detection_bp = Blueprint('detection', __name__)

@detection_bp.route('/mold', methods=['POST'])
def detect_mold():
    # TODO: Receive image, call AI model, return classification
    return jsonify({"message": "Mold detection placeholder"})