from flask import jsonify, Blueprint, abort, make_response
from flask_restful import (
    Resource,
    Api,
    reqparse,
    fields,
    marshal,
    marshal_with,
)
from category_encoders import *
import json
import tensorflow as tf
import logging
import pickle
from operator import itemgetter
from flask_cors import CORS, cross_origin
import pandas as pd
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from tensorflow.keras.preprocessing.sequence import pad_sequences
import models
import re

hoax_fields = {
    "text_new": fields.String,
    "hoax": fields.Integer,
}


class UserBase(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            "text_new",
            required=True,
            help="text_new wajib ada",
            location=["json"],
        )

    def clean_input(text):
        # remove html
        html = re.compile(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
        text = re.sub(html, "", text)

        # remove_non_ascii characters
        text = re.sub(r'[^\x00-\x7f]', r'', text)

        # remove_special_characters
        emoji_pattern = re.compile(
            '['
            u'\U0001F600-\U0001F64F'  # emoticons
            u'\U0001F300-\U0001F5FF'  # symbols & pictographs
            u'\U0001F680-\U0001F6FF'  # transport & map symbols
            u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
            u'\U00002702-\U000027B0'
            u'\U000024C2-\U0001F251'
            ']+',
            flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)

        # remove_punct
        text = re.sub(r'[]!"$%&\'()*+,./:;=#@?[\\^_`{|}~-]+', "", text)

        # lowercase text
        text = text.lower()

        return text


class Hoax(UserBase):
    def post(self):
        model = None
        model = tf.keras.models.load_model(r"./model.h5")
        args = self.reqparse.parse_args()
        text_new = args.get("text_new")
        text = UserBase.clean_input(text_new)
        # tokenize the news
        tokenizer = pickle.load(open('tokenizer.pickle', 'rb'))
        text_sequences = tokenizer.texts_to_sequences(text)
        text_padded = pad_sequences(
            text_sequences, maxlen=1313, padding='post', truncating='post')
        # prediction
        tresh = 0.55
        proba = model.predict(text_padded)
        class_id = int((proba > tresh).astype(int)[0][0])
        prob_hoax = float(proba[0][0])
        prob_valid = 1 - prob_hoax
        # models.MentalHelps.create(
        #     Age=Age,
        #     health_problems=hasil,
        # )
        return make_response(
            jsonify(
                {'teks berita': text,
                    'prediksi kelas': class_id,
                    'probabilitas hoax': prob_hoax,
                    'probabilitas valid': prob_valid}
            ),
            200,
        )


hoaxs_api = Blueprint("hoaxs", __name__)
api = Api(hoaxs_api)

api.add_resource(Hoax, "/models/predict", endpoint="predict")
