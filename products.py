from flask_restful import Resource
from flask import request, jsonify

import pandas as pd
import numpy as np
from datetime import timedelta
import json
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

class Products(Resource):
    def get(self):
        return {
            'products': ['Ice cream', 'Chocolate', 'Fruit', 'Eggs']
        }
    def post(self):
        data = request.data
        str_data = data.decode("utf-8")
        json_data = json.loads(str_data)
        print(json_data)
        df = pd.DataFrame(json_data['transactions'])
        print(df)

        data = {
            'id': df.index + 1,
            'product': df['Products'],
            'customer_id': df['Customer'],
            'driver': df['Driver'],  
            'quantity': df['Quantity'],
            'total_price': df['TotalPrice'],
            'date': df['Date']
        }

        df = pd.DataFrame(data)
        print(df)

        df['date'] = pd.to_datetime(df['date'], format='mixed')

        current_date = df['date'].max()
        customer_rfm = df.groupby('customer_id').agg({
            'date': lambda x: (current_date - x.max()).days,
            'id': 'count',
            'total_price': 'sum'
        }).rename(columns={'date': 'recency', 'id': 'frequency', 'total_price': 'monetary'})

        product_rfm = df.groupby('product').agg({
            'date': lambda x: (current_date - x.max()).days,
            'id': 'count',
            'total_price': 'sum'
        }).rename(columns={'date': 'recency', 'id': 'frequency', 'total_price': 'monetary'})

        num_clusters = 3

        # K-means clustering for customers
        kmeans_customer = KMeans(n_clusters=num_clusters, random_state=42)
        customer_rfm['customer_cluster'] = kmeans_customer.fit_predict(customer_rfm)

        # K-means clustering for products
        kmeans_product = KMeans(n_clusters=num_clusters, random_state=42)
        product_rfm['product_cluster'] = kmeans_product.fit_predict(product_rfm)

        def recommend_products_for_customer(user_id, df):
            # Check if the user ID is present in the dataset
            if user_id not in df['customer_id'].unique():
                print(f"User with ID {user_id} not found.")
                return

            # Filter transactions for the given user
            user_transactions = df[df['customer_id'] == user_id]

            # Calculate similarity between the given user and all other users based on purchase history
            user_purchase_history = df.pivot_table(index='customer_id', columns='product', values='quantity', fill_value=0)
            print(user_purchase_history)
            similarity = cosine_similarity(user_purchase_history, user_purchase_history)

            # Get indices of similar users (excluding the given user)
            similar_users_indices = np.argsort(similarity[user_id])[::-1][1:]

            # Find products bought by similar users but not bought by the given user
            recommended_products = {}
            for index in similar_users_indices:
                similar_user_transactions = df[df['customer_id'] == index]
                for product in similar_user_transactions['product'].unique():
                    if product not in user_transactions['product'].unique():
                        if product not in recommended_products:
                            recommended_products[product] = 0
                        recommended_products[product] += 1

            print(recommended_products)

            # Sort products by count in descending order and take the first 20
            recommended_products = sorted(recommended_products.items(), key=lambda x: x[1], reverse=True)[:20]

            print(f"Top 20 recommended products for user {user_id}:")

            products = []

            for product, count in recommended_products: 
                products.append(product)
            
            return products

        user_id_to_compare = json_data['user']
        products = recommend_products_for_customer(user_id_to_compare,df)
        print(products)

        if(products == None):
            return jsonify([])

        products = [int(product) for product in products]
        return jsonify(products)