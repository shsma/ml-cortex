import os
import pickle
import sys
import pandas as pd 
from typing import List

class Prediction:
    def __init__(self, category_ids: List[int], score: float, liked: bool, gender: int):
        self.category_ids = category_ids
        self.score = score
        self.liked = liked
        self.gender = gender

class PythonPredictor:
    def __init__(self, config):
        self.model = pickle.load(open('ml-gc.pkl', "rb"))
        
    
    def predict(self, payload):
        data = "[{\"g_c\": \"1 142\", \"total_hits\": 5.171922279614769}, {\"g_c\": \"1 182\", \"total_hits\": 15.635223450087942}, {\"g_c\": \"1 241\", \"total_hits\": 9.76814975539347}]"
        user_data = pd.read_json(data)
        raw_predictions = self.model.predict(user_data)
                
        if raw_predictions is None:
            return []
            
        predictions = list(
            map(
                lambda k: {
                    'category_ids': list(
                        map(int, raw_predictions.category_ids[k].split(","))
                    ),
                    'gender': int(raw_predictions.gender[k]),
                    'score': raw_predictions.score[k],
                    'liked': bool(raw_predictions.liked[k]),
                },
                raw_predictions.category_ids.keys(),
            )
        )

        return predictions
