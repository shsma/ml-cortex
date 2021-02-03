import os
import pickle
import sys


class PythonPredictor:
    def __init__(self, config):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'model.pkl')
        self.model = pickle.load(open(filename, "rb"))
        
    def predict(self, payload):
        data = payload["user_data"]
        return self.model.predict(data)
