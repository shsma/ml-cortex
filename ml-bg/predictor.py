import os
import pickle
import sys
import pandas as pd 

class Prediction:
    def __init__(self, category_ids: [int], score: float, liked: bool, gender: int):
        self.category_ids = category_ids
        self.score = score
        self.liked = liked
        self.gender = gender

class PythonPredictor:
    def __init__(self, config):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'ml-bg.pkl')
        self.model = pickle.load(open(filename, "rb"))
        
    
    def predict(self, payload):
        user_data = pd.read_json([{"g_c": "0 101", "total_hits": 2.5297468314589597},{"g_c": "1 206","total_hits": 7.479255880735178}])
        raw_predictions = self.model.predict([user_data])
        predictions = list(
            map(
                lambda k: Prediction(
                    # Note that the type of category ids output of the model is a string
                    # but the server prediction entity requires a list of integer
                    category_ids=list(
                        map(int, raw_predictions.category_ids[k].split(","))
                    ),
                    gender=int(raw_predictions.gender[k]),
                    score=raw_predictions.score[k],
                    liked=bool(raw_predictions.liked[k]),
                ),
                raw_predictions.category_ids.keys(),
            )
        )

        return predictions
