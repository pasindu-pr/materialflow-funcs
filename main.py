from flask import Flask 
from flask_restful import Resource, Api
from products import Products
from fraud import Fraud
from price import Predict
from fraud2 import Fraud2

app = Flask(__name__)
api = Api(app)

api.add_resource(Products, '/api/products')
api.add_resource(Fraud, '/api/fraud')
api.add_resource(Predict, '/api/predict')
api.add_resource(Fraud2, '/api/fraud2')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)