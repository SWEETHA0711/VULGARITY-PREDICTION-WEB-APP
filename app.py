import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import tensorflow_hub as hub
import tf_keras
import requests

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Model download and loading
MODEL_DIR = "trained-model"
MODEL_FILENAME = "tom_predict.h5"
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_FILENAME)

# Public Hugging Face file URL
HF_URL = (
    "https://huggingface.co/SWEETHA0711/vulgarity-detector/"
    f"resolve/main/{MODEL_DIR}/{MODEL_FILENAME}"
)

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Download the model if not already present
if not os.path.exists(MODEL_PATH):
    print("📥 Downloading model from Hugging Face...")
    response = requests.get(HF_URL, stream=True)
    response.raise_for_status()
    with open(MODEL_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Model downloaded successfully.")

# Load the model with custom_objects for KerasLayer
tom_predict = tf_keras.models.load_model(
    MODEL_PATH,
    custom_objects={
        "KerasLayer": lambda **kwargs: hub.KerasLayer(
            "https://tfhub.dev/google/universal-sentence-encoder/4",  # fetch from TF Hub
            trainable=False
        )
    },
)

def check_toxicity(message):
    """Run the ML model to check toxicity levels."""
    pred_probs = tom_predict.predict([message])
    return {
        "toxicity": round(pred_probs[0][0] * 100, 2),
        "severe_toxicity": round(pred_probs[0][1] * 100, 2),
        "obscene": round(pred_probs[0][2] * 100, 2),
        "threat": round(pred_probs[0][3] * 100, 2),
        "insult": round(pred_probs[0][4] * 100, 2),
        "identity_hate": round(pred_probs[0][5] * 100, 2),
    }

# Serve frontend
@app.route('/')
def index():
    return send_from_directory("public", "index.html")

# API Endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    message = data.get("sentence", "")
    if not message:
        return jsonify({"status": 400, "error": "No sentence provided!"}), 400
    return jsonify({"status": 200, "message": check_toxicity(message)})

# Socket events
users = {}

@socketio.on('register')
def handle_register(phoneNumber):
    users[request.sid] = phoneNumber

@socketio.on('chatMessage')
def handle_chat(data):
    to = data.get("to")
    msg = data.get("msg")
    if not msg or not to:
        return

    from_user = users.get(request.sid)
    summary = check_toxicity(msg)

    for sid, phone in users.items():
        if phone == to:
            if summary["toxicity"] > 40:
                socketio.emit("vulgarMessageAlert", {
                    "from": from_user,
                    "msg": msg,
                    "prediction": summary
                }, to=sid)
            else:
                socketio.emit("chatMessage", {
                    "from": from_user,
                    "msg": msg
                }, to=sid)

@socketio.on('disconnect')
def handle_disconnect():
    users.pop(request.sid, None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)








# from flask import Flask, request, jsonify, send_from_directory
# from flask_cors import CORS
# from flask_socketio import SocketIO
# import tensorflow_hub as hub
# import tf_keras

# app = Flask(__name__, static_folder="public", static_url_path="")
# CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*")

# # In-memory user storage
# users = {}

# # Load your trained model
# tom_predict = tf_keras.models.load_model(
#     "trained-model/tom_predict.h5",
#     custom_objects={"KerasLayer": hub.KerasLayer},
# )

# def check_toxicity(message):
#     """Run the ML model to check toxicity levels"""
#     pred_probs = tom_predict.predict([message])
#     return {
#         "toxicity": round(pred_probs[0][0] * 100, 2),
#         "severe_toxicity": round(pred_probs[0][1] * 100, 2),
#         "obscene": round(pred_probs[0][2] * 100, 2),
#         "threat": round(pred_probs[0][3] * 100, 2),
#         "insult": round(pred_probs[0][4] * 100, 2),
#         "identity_hate": round(pred_probs[0][5] * 100, 2),
#     }

# # Serve frontend
# @app.route('/')
# def index():
#     return send_from_directory("public", "index.html")

# # API Endpoint (optional, if you still want direct API access)
# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.get_json()
#     message = data.get("sentence", "")
#     if not message:
#         return jsonify({"status": 400, "error": "No sentence provided!"}), 400
#     summary = check_toxicity(message)
#     return jsonify({"status": 200, "message": summary})

# # Socket events
# @socketio.on('register')
# def handle_register(phoneNumber):
#     users[request.sid] = phoneNumber
#     print(f"✅ Registered user {phoneNumber} with SID {request.sid}")

# @socketio.on('chatMessage')
# def handle_chat(data):
#     to = data.get("to")
#     msg = data.get("msg")
#     if not msg or not to:
#         return
    
#     from_user = users.get(request.sid)
#     summary = check_toxicity(msg)

#     for sid, phone in users.items():
#         if phone == to:
#             if summary["toxicity"] > 40:  # threshold
#                 socketio.emit("vulgarMessageAlert", {
#                     "from": from_user,
#                     "msg": msg,
#                     "prediction": summary
#                 }, to=sid)
#             else:
#                 socketio.emit("chatMessage", {
#                     "from": from_user,
#                     "msg": msg
#                 }, to=sid)

# @socketio.on('disconnect')
# def handle_disconnect():
#     print(f"❌ User disconnected: {users.get(request.sid)}")
#     users.pop(request.sid, None)

# if __name__ == "__main__":
#     socketio.run(app, debug=True,use_reloader=False, port=5000)

# # if __name__ == '__main__':

# #     app.run(debug=True, use_reloader=False, port=5000)


