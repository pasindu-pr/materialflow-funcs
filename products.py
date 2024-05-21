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
        df = pd.DataFrame(json_data['transactions'])

        # Create structured DataFrame
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

        df['date'] = pd.to_datetime(df['date'], format='mixed')

        # RFM analysis
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

        # Clustering customers and products
        num_clusters = 3
        kmeans_customer = KMeans(n_clusters=num_clusters, random_state=42)
        customer_rfm['customer_cluster'] = kmeans_customer.fit_predict(customer_rfm)

        kmeans_product = KMeans(n_clusters=num_clusters, random_state=42)
        product_rfm['product_cluster'] = kmeans_product.fit_predict(product_rfm)

        # Add clusters to original dataframe
        df = df.merge(customer_rfm[['customer_cluster']], on='customer_id')
        df = df.merge(product_rfm[['product_cluster']], on='product')

        def recommend_products_for_customer(user_id, df, customer_rfm, product_rfm):
            if user_id not in df['customer_id'].unique():
                print(f"User with ID {user_id} not found.")
                return []

            user_cluster = customer_rfm.loc[user_id, 'customer_cluster']
            user_transactions = df[df['customer_id'] == user_id]
            user_products = set(user_transactions['product'].unique())

            # Find similar users within the same cluster
            cluster_users = df[df['customer_cluster'] == user_cluster]['customer_id'].unique()
            user_purchase_history = df[df['customer_id'].isin(cluster_users)].pivot_table(
                index='customer_id', columns='product', values='quantity', fill_value=0)
            
            if user_id not in user_purchase_history.index:
                print(f"User with ID {user_id} has no purchase history.")
                return []

            similarity = cosine_similarity(user_purchase_history)
            user_index = np.where(user_purchase_history.index == user_id)[0][0]
            similar_users_indices = np.argsort(similarity[user_index])[::-1][1:]

            recommended_products = {}
            for index in similar_users_indices:
                similar_user_id = user_purchase_history.index[index]
                similar_user_transactions = df[df['customer_id'] == similar_user_id]
                for product in similar_user_transactions['product'].unique():
                    if product not in user_products:
                        if product not in recommended_products:
                            recommended_products[product] = 0
                        recommended_products[product] += 1

            recommended_products = sorted(recommended_products.items(), key=lambda x: x[1], reverse=True)[:20]
            products = [product for product, count in recommended_products]

            return products

        user_id_to_compare = json_data['user']
        products = recommend_products_for_customer(user_id_to_compare, df, customer_rfm, product_rfm)
        print(products)

        if(products == None):
            return jsonify([])

        products = [int(product) for product in products]
        return jsonify(products)