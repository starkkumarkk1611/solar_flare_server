from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_cors import cross_origin
from numpy import convolve
from helpers import allow_file, save_file, save_curve_data, save_params
from model.model import Curve_Fitter
from model.model import convolve_curve

app = Flask(__name__)

CORS(app, resources={r'*': {'origins': '*'}})


@app.route("/", methods=['GET', 'POST'])
@cross_origin(origins=['https://solarbrustdetection.netlify.app/', "http://localhost:3000", "http://127.0.0.1:3000"])
def members():
    if (request.method == 'GET'):
        return """
            SolarFlare
            """
    if (request.method == 'POST'):
        if 'file' not in request.files:
            return "File is not selected", 400
        file = request.files['file']
        if (file.filename == ''):
            return "No file Selected", 400
        if file and allow_file(file.filename):
            filepath = save_file(file)
            a = Curve_Fitter(filepath)
            peakParams = a.params()
            curveData = convolve_curve(filepath)
            curveData['STICHEDRATE'] = a.sticher()
            curveDataPath = save_curve_data(curveData)
            PeakParamsPath = save_params(peakParams)
            with open(PeakParamsPath) as fp:
                peakParamsCsv = fp.read()
            with open(curveDataPath) as fp:
                CurveDataCsv = fp.read()
            backgroundflux = a.bdata
            print(type(backgroundflux), type(
                peakParamsCsv), type(CurveDataCsv))
            returnData = {
                "backgroundflux": str(backgroundflux),
                "peakParams": peakParamsCsv,
                "curveData": CurveDataCsv
            }

            return jsonify(returnData)
