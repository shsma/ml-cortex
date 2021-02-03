from typing import Dict


class Prediction:
    def __init__(self, brand: Dict[int, int], gender: Dict[int, int], score: Dict[int, float], liked: Dict[int, bool]):
        self.brand = brand
        self.gender = gender
        self.score = score
        self.liked = liked
