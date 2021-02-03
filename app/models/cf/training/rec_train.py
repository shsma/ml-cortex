from pandas import DataFrame
from app.entities.model.model import Model
from app.entities.trainer.trainer import Trainer

import numpy as np
from app.models.cf.rec_pred import RecPred
from implicit.nearest_neighbours import BM25Recommender
from scipy.sparse import coo_matrix
from timeutils import Stopwatch
from ssense_logger.app_logger import AppLogger


class RecTrain(Trainer):
    MODEL_PARAM = dict(params={"B": 0.85, "K": 250, "K1": 100})
    hits_data = None

    def __init__(self, app_logger: AppLogger):
        self.item_colname = "g_c"
        self.model_params = RecTrain.MODEL_PARAM["params"]
        self.app_logger = app_logger

    def train(
        self,
        hits_data: DataFrame = None,
    ) -> Model:
        self.hits_data = self._col_transform(hits_data)

        # Transform data into sparse matrix
        hits_matrix, item_dict, user_dict = self._data_mapping()

        # Create a models from the input data
        model = self._get_model()

        self.app_logger.info("Training model")

        sw = Stopwatch(start=True)

        # Train the model
        model.fit(hits_matrix, show_progress=True)

        self.app_logger.info(
            "Elapsed time of model training: {}".format(sw.elapsed.human_str())
        )

        return RecPred(model, model.similarity, item_dict, user_dict)

    def _get_model(self):
        self.app_logger.info(
            "Initializing {} model".format(BM25Recommender.__dict__["__module__"])
        )
        return BM25Recommender(**self.model_params)

    def _col_transform(self, dataset):
        dataset = dataset.copy()
        dataset["memberID"] = dataset["memberID"].astype("category")
        dataset[self.item_colname] = dataset[self.item_colname].astype("category")

        return dataset

    def _coo_transform(self):
        return coo_matrix(
            (
                self.hits_data["total_hits"].astype(np.float32),
                (
                    self.hits_data[self.item_colname].cat.codes.copy(),
                    self.hits_data["memberID"].cat.codes.copy(),
                ),
            ),
            dtype=np.float32,
        )

    def _item_to_dict(self):
        return dict(enumerate(self.hits_data[self.item_colname].cat.categories))

    def _user_to_dict(self):
        dataset = self.hits_data[["memberID"]].copy()
        dataset["user_index"] = self.hits_data["memberID"].cat.codes.copy()
        return (
            dataset[["memberID", "user_index"]]
            .drop_duplicates()
            .set_index(["memberID"])
            .to_dict()["user_index"]
        )

    def _data_mapping(self):

        # Map each item to a unique numeric value
        item_dict = self._item_to_dict()

        # Map each user to a unique numeric value
        user_dict = self._user_to_dict()

        # Create item-user matrix
        hits_matrix = self._coo_transform()

        return hits_matrix, item_dict, user_dict
