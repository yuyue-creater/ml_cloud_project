from flask import jsonify
from app import model


def predict(request):
    data = request.get_json(silent=True) or {}
    features = data.get("features")
    if features is None:
        return jsonify({"error": "Missing 'features' in request body"}), 400

    prediction = model.predict([features])
    return jsonify({"prediction": prediction.tolist()})
