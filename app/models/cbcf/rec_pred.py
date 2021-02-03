import uuid

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from app.entities.model.model import Model
from app.entities.model.prediction import Prediction
from app.utils.exception_decorator import exception_decorator


class RecPred(Model):
    MERGED_REC_PARAM = dict(n_rec=200, alpha=0.5)
    MODEL_FILE_NAME = 'bg_model.pkl'
    name = 'CBCF'
    version = '1.0'

    def __init__(self, cf_sim_mat, cf_item_dict, cb_sim_mat, cb_item_dict):
        Model.__init__(self)
        self.cf_sim_mat = cf_sim_mat
        self.cf_item_dict = cf_item_dict
        self.cb_sim_mat = cb_sim_mat
        self.cb_item_dict = cb_item_dict
        self.n_rec = RecPred.MERGED_REC_PARAM['n_rec']
        self.alpha = RecPred.MERGED_REC_PARAM['alpha']

    @staticmethod
    def _gender_processing(dataset):

        dataset = dataset.copy()
        dataset = dataset.assign(norm_score=lambda x: x.log_score / dataset.log_score.max())
        dataset.rename(columns={'norm_score': 'score'}, inplace=True)

        return dataset[['brand', 'gender', 'score', 'liked']]

    @staticmethod
    def _rescale_cb(dataset, ref_dataset) -> pd.DataFrame:

        def interp_func(x, lb):
            return ((x - min(x)) / (1 - min(x))) * (1 - lb) + lb

        dataset_out = pd.DataFrame()

        for gender in dataset.gender.unique():

            dataset_sub = dataset[dataset.gender == gender].copy()

            if dataset_sub.empty:
                continue

            lower_bound = ref_dataset.groupby('gender')['score'].apply(min)[gender]

            dataset_sub = dataset_sub.assign(score=lambda x: interp_func(x['score'], lb=lower_bound))

            dataset_out = dataset_out.append(dataset_sub)

        return dataset_out.sort_values(by='score', ascending=False).reset_index()

    def _post_process_rec(self, dataset):
        """
        Process recommendation list
        :param dataset
        :return dataset
        """
        request_id = str(uuid.uuid1())

        dataset = dataset.assign(log_score=lambda x: np.log1p(x.score))
        dataset.drop(columns=['score'], axis=1, inplace=True)

        dataset.brand = dataset.brand.astype('int16')
        dataset.gender = dataset.gender.astype('int8')

        proc_dataset = pd.DataFrame()
        for gender in dataset.gender.unique():
            dataset_gender = dataset[dataset.gender == gender].head(self.n_rec).copy()
            dataset_gender = RecPred._gender_processing(dataset_gender)
            proc_dataset = proc_dataset.append(dataset_gender, sort=False)

        proc_dataset.sort_values(by='score', ascending=False, inplace=True)
        proc_dataset.reset_index(inplace=True, drop=True)

        proc_dataset.score = np.round(proc_dataset.score, decimals=6)

        return proc_dataset

    @staticmethod
    def _rec_filter(cf_rec, cb_rec):

        return cf_rec.set_index(['brand', 'gender']).join(cb_rec.set_index(['brand', 'gender']), how='outer',
                                                          lsuffix='_cf', rsuffix='_cb')

    @exception_decorator
    def _rec_predict(self, user_data, sim_mat: csr_matrix, item_dict: dict):

        """
        :return recommendations for each user in the dataset
        """

        user_data_dict = dict(zip(user_data.b_g, user_data.total_hits))

        user_items = np.array([user_data_dict.get(item_dict.get(k), 0) for k in item_dict.keys()])

        user_items = user_items.reshape(1, -1)
        user_items = csr_matrix(user_items)

        # Compute dot product
        rec_mat = user_items @ sim_mat

        result = []
        liked = set(user_items.indices)
        user_indices, user_scores = rec_mat.indices, rec_mat.data
        best = sorted(zip(user_indices, user_scores), key=lambda x: -x[1])
        tagged_best = [rec + (True,) if rec[0] in liked else rec + (False,) for rec in best]
        result.extend([(item_dict[rid].split(' ')[0], item_dict[rid].split(' ')[1],
                        score, flag_brx) for rid, score, flag_brx in tagged_best])

        rec = pd.DataFrame(result, columns=['brand', 'gender', 'score', 'liked'])

        if rec.score.lt(0).any():
            return pd.DataFrame(columns=['brand', 'gender', 'score', 'liked'])

        if len(rec.index) == 0:
            return pd.DataFrame(columns=['brand', 'gender', 'score', 'liked'])

        return self._post_process_rec(rec)

    @exception_decorator
    def _rec_agg(self, cf_rec: pd.DataFrame, cb_rec: pd.DataFrame):

        cbf = RecPred._rec_filter(cf_rec, cb_rec)

        cbf.reset_index(inplace=True)
        cbf.liked_cf.fillna(cbf.liked_cb, inplace=True)
        cbf.liked_cb.fillna(cbf.liked_cf, inplace=True)
        cbf = cbf.assign(score=lambda x: np.where(x.score_cf.isnull(),
                                                  x.score_cb,
                                                  np.where(
                                                      x.score_cb.isnull(),
                                                      x.score_cf,
                                                      ((self.alpha * x.score_cb) + ((1 - self.alpha) * x.score_cf)))),
                         liked=lambda x: np.where(x.liked_cf == x.liked_cb, x.liked_cf, x.liked_cf)
                         )
        cbf.sort_values(by='score', ascending=False, inplace=True)

        cbf.reset_index(drop=True, inplace=True)

        cbf = cbf[['brand', 'gender', 'score', 'liked']]

        if cbf.score.lt(0).any():
            return pd.DataFrame(columns=['brand', 'gender', 'score', 'liked'])

        return cbf

    @exception_decorator
    def predict(self, data) -> Prediction:
        cf_rec = self._rec_predict(data, sim_mat=self.cf_sim_mat, item_dict=self.cf_item_dict)
        cb_rec = self._rec_predict(data, sim_mat=self.cb_sim_mat, item_dict=self.cb_item_dict)
        cb_rec = self._rescale_cb(cb_rec, cf_rec)
        rec_dict = self._rec_agg(cf_rec, cb_rec).to_dict()
        return Prediction(rec_dict['brand'], rec_dict['gender'], rec_dict['score'], rec_dict['liked'])
