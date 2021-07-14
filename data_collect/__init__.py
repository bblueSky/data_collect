from data_collect.cameraCalibration.views import  cameraCalibration

from  flask import Flask,render_template,request,Blueprint , jsonify


def create_app():
    app = Flask(__name__)
    app.register_blueprint(cameraCalibration,url_prefix='/cameraCalibration')

    return app