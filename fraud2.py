from flask import Flask, request
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from flask_restful import Resource
from flask import jsonify
import json

app = Flask(__name__)

class Fraud2(Resource):
    def post(self):
        data = request.data
        str_data = data.decode("utf-8")
        data = json.loads(str_data) 

        print(data)

        customer_data = pd.DataFrame(data['customer_data'])
        transaction_data = pd.DataFrame(data['transaction_data'])
        new_order = data['new_order']

        # ----------------   Customer Dataset -----------------------
        customer_features = ['customer_id', 'customer_type', 'hometown']
        customer_cluster_data = customer_data[customer_features]

        label_encoder = LabelEncoder()
        customer_cluster_data['customer_type'] = label_encoder.fit_transform(customer_cluster_data['customer_type'])
        customer_cluster_data['hometown'] = label_encoder.fit_transform(customer_cluster_data['hometown'])

        scaler = StandardScaler()
        customer_cluster_data_scaled = scaler.fit_transform(customer_cluster_data)

        kmeans_customer = KMeans(n_clusters=3, random_state=42)
        customer_cluster_data['customer_cluster'] = kmeans_customer.fit_predict(customer_cluster_data_scaled)

        # ----------------   Transaction Dataset  -----------------------
        transaction_features = ['customer_id', 'product_id', 'quantity', 'total_price']
        transaction_cluster_data = transaction_data[transaction_features]

        transaction_cluster_data['total_price'] = transaction_cluster_data['total_price'].astype(float)

        imputer = SimpleImputer(strategy='mean')
        transaction_cluster_data_scaled_imputed = imputer.fit_transform(transaction_cluster_data.drop('customer_id', axis=1))

        kmeans_transaction = KMeans(n_clusters=3, random_state=42)
        transaction_cluster_data['transaction_cluster'] = kmeans_transaction.fit_predict(transaction_cluster_data_scaled_imputed)

        # --------------------   Merge customer clusters with transaction clusters based on customer_id --------------------------------
        merged_data = pd.merge(customer_cluster_data, transaction_cluster_data, on='customer_id')

        # Analyze connectivity
        transaction_distribution = merged_data.groupby(['customer_cluster', 'transaction_cluster']).size().unstack(fill_value=0)

        # Step 1: Manually create a new order
        new_order = {
            'customer_id': 9309,
            'product_id': 444,
            'quantity': 2,
            'total_price': 100.0
        }

        # Step 2: Get the customer's cluster based on their ID
        customer_id = new_order['customer_id']

        orderStatus = False

        # Check if the customer ID exists in the dataset
        if customer_id in merged_data['customer_id'].values:
            customer_cluster = merged_data[merged_data['customer_id'] == customer_id]['customer_cluster'].iloc[0]

            # Step 3: Retrieve the transaction cluster for the product based on its ID
            product_id = new_order['product_id']

            # Check if the product ID exists in the dataset
            if product_id in merged_data['product_id'].values:
                transaction_cluster = merged_data[merged_data['product_id'] == product_id]['transaction_cluster'].iloc[0]

                # Step 4: Compare the customer's cluster with the transaction cluster
                if customer_cluster == transaction_cluster:
                    orderStatus = True
                else:
                    orderStatus = False
            else:
                orderStatus = False
        else:
            orderStatus = False

        return jsonify(orderStatus)