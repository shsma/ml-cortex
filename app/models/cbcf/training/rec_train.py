from pathlib import Path
from typing import Tuple
from pandas import DataFrame

from app.entities.model.model import Model
from app.entities.trainer.trainer import Trainer
from app.models.cbcf.training.cb_train import ContTrain
from app.models.cbcf.training.cf_train import CollabTrain
from app.models.cbcf.rec_pred import RecPred
from app.utils.serialization import load_pickle


class RecTrain(Trainer):

    def train(self, hits_data: DataFrame = None, products_data: DataFrame = None) -> Model:
        if hits_data is None or products_data is None:
            data = RecTrain._load_data_local()
            hits_data, products_data = data[0], data[1]

        cf_sim_mat, cf_item_dict = CollabTrain(hits_data).fit()

        cb_sim_mat, cb_item_dict = ContTrain(products_data).fit()

        rec_pred = RecPred(cf_sim_mat=cf_sim_mat,
                           cf_item_dict=cf_item_dict,
                           cb_sim_mat=cb_sim_mat,
                           cb_item_dict=cb_item_dict,
                           )

        return rec_pred

    @staticmethod
    def _load_data_local() -> Tuple:
        hits_data = load_pickle(directory=Path('./shared/'), name='hits_df.pkl')
        products_data = load_pickle(directory=Path('./shared/'), name='products_df.pkl')

        return hits_data, products_data
