import tensorflow_hub as hub
import tf_keras

tom_predict = tf_keras.models.load_model(
    "trained-model/tom_predict.h5",
    custom_objects={"KerasLayer": hub.KerasLayer},
)
# tom_predict.summary()
print("the summary is:",tom_predict.summary())


def insert_prediction_values(sentence):
    pred_probs = tom_predict.predict([sentence])
    pred_summary = {
        "toxicity": round(pred_probs[0][0] * 100, 2),
        "severe_toxicity": round(pred_probs[0][1] * 100, 2),
        "obscene": round(pred_probs[0][2] * 100, 2),
        "threat": round(pred_probs[0][3] * 100, 2),
        "insult": round(pred_probs[0][4] * 100, 2),
        "identity_hate": round(pred_probs[0][5] * 100, 2),
    }
    print(f"{sentence}: {pred_summary}")

insert_prediction_values('Hello nigga!')
insert_prediction_values('Shut the fuck up!')
insert_prediction_values('A man rides a horse. And it\'s beautiful.')
insert_prediction_values('I dont want to talk to you. Go away!')
insert_prediction_values('I wish you were dead!')
insert_prediction_values('That cat is soo cute!')
