import pickle
import sys
import pandas as pd 

class Prediction:
    brand_id: int
    score: float
    liked: bool
    gender: int

    def __init__(self, brand_id: int, score: float, liked: bool, gender: int):
        self.brand_id = brand_id
        self.score = score
        self.liked = liked
        self.gender = gender

class PythonPredictor:
    def __init__(self, config):
        self.model = pickle.load(open('ml-bg.pkl', "rb"))
        
    
    def predict(self, payload):
        user_data = pd.read_json("[{\"b_g\": \"425 0\", \"total_hits\": 0.10170139230422684}]")
        raw_predictions = self.model.predict(user_data)
        
        if raw_predictions is None:
            return []
            
        
        predictions = list(map(
            lambda k: {
                'brand_id': raw_predictions.brand[k],
                'gender': raw_predictions.gender[k],
                'score': raw_predictions.score[k],
                'liked': raw_predictions.liked[k]
            },
            raw_predictions.brand.keys()))
            

        return predictions
