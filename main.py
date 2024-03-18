from flask import Flask 
from flask_restful import Resource, Api
from products import Products
from fraud import Fraud
from price import Predict

app = Flask(__name__)
api = Api(app)

api.add_resource(Products, '/api/products')
api.add_resource(Fraud, '/api/fraud')
api.add_resource(Predict, '/api/predict')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)