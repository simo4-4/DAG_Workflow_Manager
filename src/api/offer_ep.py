from .prediction_ep import Prediction


def get_offer(prediction: Prediction) -> dict:
    if prediction.ats_prediction * prediction.resp_prediction >= 200:
        result = "OFFER_2"
    else:
        result = "OFFER_1"
    return {"offer": result}
