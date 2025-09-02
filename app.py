# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import tensorflow_hub as hub
# import tf_keras

# app = Flask(__name__)
# CORS(app)  # ✅ allow requests from different ports (4000 → 5000)

# # Load model
# tom_predict = tf_keras.models.load_model(
#     "trained-model/tom_predict.h5",
#     custom_objects={"KerasLayer": hub.KerasLayer},
# )

# def check_toxicity(message):
#     pred_probs = tom_predict.predict([message])
#     return pred_probs[0]

# @app.route('/predict', methods=['POST'])
# def handle_send_message():
#     try:
#         data = request.get_json()
#         message = data.get('sentence')

#         if not message:
#             return jsonify({"status": 400, "error": "No sentence provided!"}), 400

#         toxicity_scores = check_toxicity(message)

#         summary = {
#             "toxicity": round(toxicity_scores[0] * 100, 2),
#             "severe_toxicity": round(toxicity_scores[1] * 100, 2),
#             "obscene": round(toxicity_scores[2] * 100, 2),
#             "threat": round(toxicity_scores[3] * 100, 2),
#             "insult": round(toxicity_scores[4] * 100, 2),
#             "identity_hate": round(toxicity_scores[5] * 100, 2),
#         }

#         return jsonify({"status": 200, "message": summary})

#     except Exception as e:
#         import traceback
#         print("🔥 Flask API Error:", traceback.format_exc())
#         return jsonify({"status": 500, "error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False, port=5000)



from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import tensorflow_hub as hub
import tf_keras

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory user storage
users = {}

# Load your trained model
tom_predict = tf_keras.models.load_model(
    "trained-model/tom_predict.h5",
    custom_objects={"KerasLayer": hub.KerasLayer},
)

def check_toxicity(message):
    """Run the ML model to check toxicity levels"""
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

# API Endpoint (optional, if you still want direct API access)
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    message = data.get("sentence", "")
    if not message:
        return jsonify({"status": 400, "error": "No sentence provided!"}), 400
    summary = check_toxicity(message)
    return jsonify({"status": 200, "message": summary})

# Socket events
@socketio.on('register')
def handle_register(phoneNumber):
    users[request.sid] = phoneNumber
    print(f"✅ Registered user {phoneNumber} with SID {request.sid}")

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
            if summary["toxicity"] > 40:  # threshold
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
    print(f"❌ User disconnected: {users.get(request.sid)}")
    users.pop(request.sid, None)

if __name__ == "__main__":
    socketio.run(app, debug=True,use_reloader=False, port=5000)

# if __name__ == '__main__':
#     app.run(debug=True, use_reloader=False, port=5000)