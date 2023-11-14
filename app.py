# import library
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import gevent.pywsgi
import logging
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    get_jwt,
    get_jwt_identity,
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)
from datetime import datetime, timedelta, timezone

# import module
import models
from resources.hoaxs import hoaxs_api


# inisiasi object flask
app = Flask(__name__)
CORS(app, allow_headers=["Content-Type"])
# ACCESS_TOKEN_JWT
app.config["JWT_SECRET_KEY"] = "apihoax"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.register_blueprint(hoaxs_api, url_prefix="/v1")
jwt = JWTManager(app)
logging.basicConfig(level=logging.INFO)


@app.get("/")
def home():
    return "hello hoax api"


if __name__ == "__main__":
    models.initialize()
    # Untuk mode pengembangan
    app.run(debug=True, host="0.0.0.0", port=80)
    # Gunakan wsgi server untuk deployment (production)
    # http_server = gevent.pywsgi.WSGIServer(("127.0.0.1", 80), app)
    # http_server.serve_forever()
