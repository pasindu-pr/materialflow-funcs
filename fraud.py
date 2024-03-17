from flask_restful import Resource
from flask import request
import joblib
 
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load the trained model
clf = joblib.load("./models/random_forest_model.pkl")

class Fraud(Resource):
    def post():
        data = request.get_json()   
        sample_df = pd.DataFrame(data) 

        # Preprocess the sample data
        sample_df['total_price'] = sample_df['total_price'].str.replace('Rs. ', '').astype(float)
        sample_df = pd.get_dummies(sample_df)

        # Load the training data
        datset = pd.read_csv("/data/detected-frauds.csv")
        
        X = pd.get_dummies(datset.drop('is_fraud', axis=1))

        # Split the data into features (X) and target variable (y)
        y = datset['is_fraud']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Ensure that the sample data has the same columns as the training data
        missing_cols = set(X_train.columns) - set(sample_df.columns)
        for col in missing_cols:
            sample_df[col] = 0

        # Reorder columns to match the order of the training data
        sample_df = sample_df[X_train.columns]

        # Use the trained model to predict
        prediction = clf.predict(sample_df)

        # Prepare response
        if prediction[0] == 1:
            result = True
        else:
            result = False

        return jsonify(result)