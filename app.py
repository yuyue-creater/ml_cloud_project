from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Load the model using absolute path
model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
model = joblib.load(model_path)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    features = data["features"]
    prediction = model.predict([features])
    return jsonify({"prediction": prediction.tolist()})

port = int(os.environ.get("PORT", 8080))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)