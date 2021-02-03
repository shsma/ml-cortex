class CustomerInteraction:
    """
    This class represents the customer interaction data
    needed to calculate the score for prediction
    """
    def __init__(self,
                 customer_id: int,
                 date: str,
                 gender: int,
                 brand_id: int,
                 flag_purchase: int,
                 flag_added: int,
                 total_hits: int):
        self.customer_id = customer_id
        self.date = date  # date of interaction
        self.gender = gender  # men=1, women=0
        self.brand_id = brand_id  # brand id
        self.flag_purchase = flag_purchase  # 1 if the product was purchased 0 if it wasn't
        self.flag_added = flag_added  # 1 if the product was added to wish-list or cart 0 if it wasn't
        self.total_hits = total_hits  # number of product views

    def to_dict(self):
        return {
            'customer_id': self.customer_id,
            'date': self.date,
            'gender': self.gender,
            'brand_id': self.brand_id,
            'purchased': self.flag_purchase,
            'add_to_wishlist': self.flag_added,
            'add_to_cart': self.flag_added,
            'views': self.total_hits,
        }
