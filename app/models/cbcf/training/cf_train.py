"""
@name: calibration.py
@author: Mohammad Jeihoonian
Created on July 2019
"""
import numpy as np
from implicit.nearest_neighbours import BM25Recommender
from scipy.sparse import coo_matrix


class CollabTrain(object):

    def __init__(self, hits_data):
        self.hits_data = hits_data
        self.item_colname = 'b_g'
        self.model_params = {'B': 0.75, 'K': 250, 'K1': 100}
        self.model = None

    def coo_transform(self, dataset):

        return coo_matrix((dataset['total_hits'].astype(np.float64),
                           (dataset[self.item_colname].cat.codes.copy(),
                            dataset['memberID'].cat.codes.copy())), dtype=np.float64)

    def item_mapping(self, dataset):

        # Map each item and user to a unique numeric value
        dataset = dataset.copy()
        dataset['memberID'] = dataset['memberID'].astype('category')
        dataset[self.item_colname] = dataset[self.item_colname].astype('category')

        # item dictionary
        item_dict = dict(enumerate(dataset[self.item_colname].cat.categories))

        hits_matrix = self.coo_transform(dataset)

        return hits_matrix, item_dict

    def transform_data(self):

        # Read in triples of user/item/hits from the input dataset
        # Get a model based off the input params

        return self.item_mapping(dataset=self.hits_data)

    def get_model(self):

        return BM25Recommender(**self.model_params)

    def fit(self):

        # Transform data into sparse matrix
        hits_matrix, item_dict = self.transform_data()

        # Create the model from the input data
        self.model = self.get_model()

        self.model.fit(hits_matrix, show_progress=True)

        return self.model.similarity, item_dict
