
"""
@name: cb_train.py

@author: Graydon Snider

Created on Nov 2019
"""
import datetime
import pandas as pd
from scipy.sparse import csr_matrix

from app.models.cbcf.helpers.cb_helper_function import get_text_distance, cb_manipulate_text, CB_REC_PARAM


class ContTrain(object):

    def __init__(self, product_data: pd.DataFrame):

        self.product_data = product_data

    def fit(self):

        assert self.product_data.shape[0] > 0

        # transforms cleaned-up descriptions into csr matrix

        # get time span for fit
        last_n_weeks = CB_REC_PARAM['max_product_age_weeks']

        start_date = (datetime.date.today() - datetime.timedelta(weeks=last_n_weeks)).strftime('%Y-%m-%d')
        end_date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        # convert product df to brand df
        brand_df = cb_manipulate_text(self.product_data,
                                      start_date=start_date,
                                      end_date=end_date)

        # create two dictionaries of codes
        brand_df['bg_codes'] = brand_df['b_g'].cat.codes
        cb_item_dict = dict(zip(brand_df['bg_codes'], brand_df['b_g']))

        # Create a sparse matrix of all the brands, per gender
        new = brand_df["b_g"].str.split(" ", n=1, expand=True)
        brand_df["gender"] = new[1]

        weights_inner: pd.DataFrame = pd.DataFrame()

        for gender in brand_df.gender.unique():

            dataset_sub = brand_df.copy()
            dataset_sub = dataset_sub[dataset_sub['gender'] == gender]

            # extract 1 minus cosine distance between bg texts
            weights_inner_sub = get_text_distance(corpus_in=list(dataset_sub['description']),
                                                  stock_in=dataset_sub['stockForSale'],
                                                  docids_in=dataset_sub['bg_codes'])

            weights_inner = pd.merge(weights_inner, weights_inner_sub,
                                     left_index=True, right_index=True, how='outer')

        weights_inner.fillna(0, inplace=True)
        weights_inner.sort_index(axis=0, inplace=True)
        weights_inner.sort_index(axis=1, inplace=True)

        # convert to sparse for efficiency
        cb_sim_mat = csr_matrix(weights_inner)

        return cb_sim_mat, cb_item_dict
