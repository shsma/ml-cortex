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
