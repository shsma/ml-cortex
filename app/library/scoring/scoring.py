import pandas as pd
import numpy as np
from pandas import DataFrame


class Scoring:
    """
    Class to calculate brand gender score based on user history
    Scoring Config details:
        last_n_weeks: int # Number of weeks of data
        p_weight: Union[float, int]  # Weight used to score purchased product
        w_weight: Union[float, int]  # Weight used to score not purchased product added to wishlist or cart
        decay_weight: Union[float, int] # Coefficient to calculate decay
        decay_weight_multiplier: Union[float, int] # Coefficient to calculate decay
    """

    def __init__(self,
                 last_n_weeks: int,
                 p_weight: float,
                 w_weight: float,
                 decay_weight: float,
                 decay_weight_multiplier: float):
        self._config = {'last_n_weeks': last_n_weeks,
                        'p_weight': p_weight,
                        'w_weight': w_weight,
                        'decay_weight': decay_weight,
                        'decay_weight_multiplier': decay_weight_multiplier
                        }

    def _get_decay_rate(self) -> float:
        """
        Decay formula
        """
        decay_weight = self._config['decay_weight']
        decay_weight_multiplier = self._config['decay_weight_multiplier']
        last_n_weeks = self._config['last_n_weeks']
        return 1 / (decay_weight * decay_weight_multiplier * last_n_weeks)

    def score_history(self, customer_interactions: DataFrame) -> DataFrame:
        """
            This method contain the logic to calculate brand gender score from a list of CustomerInteraction
            - brands purchased and added to the wish list are scored with specific weight
            - time decay is applied to the score
            - data is group by customer_id and score is sum
            It should receive as input a DataFrame with the following structure:
            ['product_id', 'date', 'brand_id', 'gender', 'views', 'purchased',
            'add_to_cart', 'add_to_wishlist', 'time_on_page']

            :return: DataFrame: ['memberID', 'b_g', 'total_hits']
        """

        if customer_interactions.size < 1:
            raise Exception('Can not score empty user interactions.')

        # Combine brand and gender into one column
        customer_interactions['b_g'] = customer_interactions \
            .apply(lambda x: str(x.brand_id) + ' ' + str(x.gender), axis=1)

        # ==================== Weight users-items interactions ============== #

        # set views value for product purchased (purchased==1)
        customer_interactions.loc[customer_interactions.purchased == 1, 'views'] = \
            self._config['p_weight'] * customer_interactions[customer_interactions.purchased == 1]['views']

        # set views value for product added to wishlist or cart but not purchased  (purchased!=1)
        customer_interactions.loc[((customer_interactions.add_to_wishlist == 1)
                                   | (customer_interactions.add_to_cart == 1))
                                  & (customer_interactions.purchased != 1), 'views'] = \
            self._config['w_weight'] * customer_interactions[((customer_interactions.add_to_wishlist == 1)
                                                              | (customer_interactions.add_to_cart == 1))
                                                             & (customer_interactions.purchased != 1)]['views']

        # ==================== Apply time decay function ==================== #

        # Convert string date to datetime
        customer_interactions.date = pd.to_datetime(customer_interactions.date)
        # add a new column decay_date on the data frame with the decay function
        last_browsing_date = pd.to_datetime('now')
        customer_interactions = customer_interactions.assign(decay_date=lambda x: (last_browsing_date - x.date)
                                                             .astype('timedelta64[D]')
                                                             .astype('int'))

        # add a new column decay calculated from decay_date and views
        decay_rate = self._get_decay_rate()
        customer_interactions = customer_interactions.assign(
            decay=lambda x: x.views * np.exp(-decay_rate * x.decay_date))

        # ==================== Aggregate and shape dataset ================= #

        # Group the dataset by customer_id, brand, gender sum the decay and rename it to views
        customer_interactions = customer_interactions.groupby(['customer_id', 'b_g']) \
            .decay.sum() \
            .rename('views') \
            .reset_index()

        # remove unnecessary column
        customer_interactions = customer_interactions[['customer_id', 'b_g', 'views']]
        # rename columns to match model expectation
        customer_interactions = customer_interactions.rename(columns={'customer_id': 'memberID'})
        customer_interactions = customer_interactions.rename(columns={'views': 'total_hits'})

        return customer_interactions
