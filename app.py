from flask import Flask, request, jsonify
import joblib
import os

app = Flask(__name__)

# Load the trained model
model_path = os.path.join(os.getcwd(), "model.pkl")
model = joblib.load(model_path)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    features = data["features"]  # Expecting a list
    prediction = model.predict([features])
    return jsonify({"prediction": prediction.tolist()})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)