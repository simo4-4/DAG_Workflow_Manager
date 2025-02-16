from fastapi import FastAPI
from .prediction_ep import predict_ats, predict_resp, Prediction
from .offer_ep import get_offer
from .member_features import MemberFeatures

app = FastAPI()


@app.get("/")
async def ping():
    return {"msg": "pong"}


@app.post("/ml/ats/predict")
async def predict_ats_ep(member_features: MemberFeatures):
    return predict_ats(member_features)


@app.post("/ml/resp/predict")
async def predict_resp_ep(member_features: MemberFeatures):
    return predict_resp(member_features)


@app.post("/offer/assign")
async def assign_offer_ep(prediction: Prediction):
    return get_offer(prediction)
