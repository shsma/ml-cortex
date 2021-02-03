import numpy as np
from pandas import DataFrame
from scipy.sparse import coo_matrix
from timeutils import Stopwatch
from implicit.nearest_neighbours import BM25Recommender
from ssense_logger.app_logger import AppLogger
from app.config import Config


class CollabTrain(object):
    def __init__(self, hits_data: DataFrame):
        self.hits_data = hits_data
        self.item_colname = "b_g_c"
        self.model_params = {"B": 0.75, "K": 250, "K1": 100}
        self.model = None
        self.app_logger = AppLogger(app_name=Config.APP_NAME, env=Config.ENV)

    def coo_transform(self, dataset, userCol="memberID", countCol="total_hits"):

        return coo_matrix(
            (
                dataset[countCol].astype(np.float64),
                (
                    dataset[self.item_colname].cat.codes.copy(),
                    dataset[userCol].cat.codes.copy(),
                ),
            ),
            dtype=np.float64,
        )

    def item_mapping(self, dataset, userCol="memberID"):

        # Map each item and user to a unique numeric value
        dataset = dataset.copy()
        dataset[userCol] = dataset[userCol].astype("category")
        dataset[self.item_colname] = dataset[self.item_colname].astype("category")

        # item dictionary
        item_dict = dict(enumerate(dataset[self.item_colname].cat.categories))

        hits_matrix = self.coo_transform(dataset)

        return hits_matrix, item_dict

    def transform_data(self):

        # Read in triples of user/item/hits from the input dataset

        self.app_logger.info(msg="Transforming user data")

        return self.item_mapping(dataset=self.hits_data)

    def get_model(self):

        # Get a model based off the input params

        self.app_logger.info(msg="Initializing the nearest neighbors model")

        return BM25Recommender(**self.model_params)

    def fit(self):

        # Transform data into sparse matrix
        hits_matrix, item_dict = self.transform_data()

        # Create a models from the input data
        self.model = self.get_model()

        self.app_logger.info(msg="Training the nearest neighbors model")

        sw = Stopwatch(start=True)

        self.model.fit(hits_matrix, show_progress=True)

        self.app_logger.info(
            msg="Elapsed time of model training: {}".format(sw.elapsed.human_str())
        )

        return self.model.similarity, item_dict
