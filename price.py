from flask_restful import Resource
from flask import request
import joblib
 
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import pickle

class Predict(Resource):
    def post(self):
        data = request.get_json()
        retail_price = data.get('retail_price', '20000')
        if retail_price == '':
          retail_price = '20000'
        product_name = data['product_name']
        brand = data['brand']
        sub_category = data['sub_category']
        category = data.get('category', 'paint')

        feature_list = []
        feature_list.append(float(retail_price))

        
        sub_category_list = [
            "anticorrosive",
            "auto_filler",
            "auto_paint",
            "auto_primer",
            "black_board_&_paints",
            "chinese_lacquer",
            "decorative_paints",
            "enamel_paint",
            "floor_paint",
            "floor_polish",
            "interior_paint",
            "paint_accessories",
            "paint_brush",
            "paints_preparation",
            "shield_paint",
            "solid_colors",
            "thinner",
            "toa_spray_paints",
            "wall_filler_&_putty",
            "wood_lacquer_&_varnish",
            "wood_preservative",
            "wood_putty",
            "wood_stain",
        ]

        product_name_list = ["scraper_rhp",
            "classic_paint_brush_harris"
            "s171_universal_thinner_1l_causeway",
            "black_board_paint_black_1l_kenlux",
            "blue_nax_super_high_performance_clear_1l",
            "brilliant_white_101a_auto_sunny_500ml",
            "brilliant_white_1l_luxury_glo_9102a",
            "brilliant_white_1l_luxury_shield_9102a",
            "brown_anticorrosive_ac06_1l_kenlux",
            "chinese_lacquer_100ml_deltex",
            "dark_green_12_s_p_toa",
            "floor_polish_red_400g_roya",
            "ici_general_purpose_stoper_1kg",
            "mahogany_enamel_1509_1l_kenlux",
            "paint_remover_190ml",
            "red_floor_paint_qd02_1l_kenlux",
            "sf_supiri_metal_filler_hardener_450g",
            "spray_gun_f75g_13mm__14mm_voylet",
            "wb_wood_putty_17_teak_250g_jat",
            "wall_filler_luxury_1l_causeway",
            "wood_lacquer_satin_1l_f5588_sunny",
            "zinc_phosphate_qd_primer_black_1l_brand_amt"
        ]   
    
        brand_list = [
            "amt",
            "causeway_paints",
            "deltex",
            "dulux",
            "harris",
            "jat",
            "nippon",
            "royal",
            "sf_supiri",
            "sayerlack",
            "toa",
            "voylet"
        ]

        category_list = ["paint"]
        

        def traverse(lst,value):
            for item in lst:
                if item == value:
                    feature_list.append(1)
                else:
                    feature_list.append(0)

        traverse(product_name_list,product_name)
        traverse(brand_list,brand)
        traverse(sub_category_list,sub_category)
        traverse(category_list,category)

        pred = self.prediction(feature_list)

        newCurrentWholesalePrice = float(retail_price) - float(retail_price) * 0.25
        newFutureWholesalePrice = pred - pred * 0.25

        sellerCurrentProfit = float(retail_price) - float(newCurrentWholesalePrice)
        sellerFutureProfit = pred - newFutureWholesalePrice

        earlyPurchaseExpectProfit = 0
        
        if sellerCurrentProfit < sellerFutureProfit:
            earlyPurchaseExpectProfit = pred - newCurrentWholesalePrice

        extraProfitFromEarlyPurchase = earlyPurchaseExpectProfit - sellerFutureProfit
        
        message = "Seller might need to Hold the Need to get Action for the Rest of the purchases" if extraProfitFromEarlyPurchase == 0 else "Early purchasing and make inventory high and it’s keep for next month"

        print(retail_price)
        print(pred)
        print(newCurrentWholesalePrice)
        print(newFutureWholesalePrice)
        print(sellerCurrentProfit)
        print(sellerFutureProfit)
        print(earlyPurchaseExpectProfit)
        print(extraProfitFromEarlyPurchase) 

        return jsonify({'prediction': pred, 'extraProfitFromEarlyPurchase': extraProfitFromEarlyPurchase, 'message': message})

    @staticmethod
    def prediction(lst):
        filename = 'models/predictor.pickle'
        with open(filename, 'rb') as file:
            model = pickle.load(file)
        pred_value = model.predict([lst])
        return pred_value[0]