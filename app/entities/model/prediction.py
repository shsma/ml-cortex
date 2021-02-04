from typing import Dict


class Prediction:
    def __init__(
        self, 
        brand: Dict[int, int]=None,
        gender: Dict[int, int]=None,
        score: Dict[int, float]=None,
        liked: Dict[int, bool]=None,
        category_ids: Dict[int, str]=None,
        ):
        self.brand = brand
        self.gender = gender
        self.score = score
        self.liked = liked
        self.category_ids = category_ids

