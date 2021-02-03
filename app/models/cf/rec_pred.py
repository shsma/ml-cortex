import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

from app.entities.model.model import Model
from app.entities.model.prediction import Prediction


# Note that the dataframe column name "category"
# actually refers to a list of category ids comma delimited
# https://github.com/Groupe-Atallah/datascience-recommendation/blob/master/gendercategory/data_prep.py#L99
class RecPred(Model):
    REC_PARAM = dict(n_rec=100)
    MODEL_FILE_NAME = "gc_model.pkl"
    name = "CF"
    version = "1.0"

    def __init__(self, model, sim_mat, item_dict, user_dict):
        Model.__init__(self)
        self.model = model
        self.sim_mat = sim_mat
        self.item_dict = item_dict
        # training has its own index
        # item_dict contains the link between the training ids and the "gender category" cominations
        # {
        #   0: '0 100'
        # }
        self.user_dict = user_dict
        self.item_colname = "g_c"
        self.n_rec = RecPred.REC_PARAM["n_rec"]

    def predict(self, data) -> Prediction:
        # Create a sparse matrix of shape (number_users, number_items)
        user_data_dict = dict(zip(data[self.item_colname], data.total_hits))
        #    {
        #    '0 659': 0.1234
        #   }
        user_items = [
            user_data_dict.get(self.item_dict.get(k), 0)  # default value
            for k in self.item_dict.keys()
        ]
        user_items = csr_matrix(user_items)

        # Compute dot product https://numpy.org/doc/stable/reference/generated/numpy.dot.html
        rec_mat = user_items @ self.sim_mat

        # Calculate the top N items, removing the users own liked items from the results
        result = list()
        liked = set(user_items.indices)
        user_indices, user_scores = rec_mat.indices, rec_mat.data
        best = sorted(zip(user_indices, user_scores), key=lambda x: -x[1])
        tagged_best = [
            rec + (True,) if rec[0] in liked else rec + (False,) for rec in best
        ][: self.n_rec]

        # Creation of the top n recommendations df
        result.extend(
            [
                (
                    self.item_dict[rid].split(" ")[0],  # gender
                    self.item_dict[rid].split(" ")[1],  # category
                    score,  # score
                    flag_brx,  # liked
                )
                for rid, score, flag_brx in tagged_best
            ]
        )
        rec = pd.DataFrame(result, columns=["gender", "category", "score", "liked"])

        if rec.empty:
            return rec.rename(columns={"category": "category_ids"})

        # Score normalization and reorder
        rec = RecPred._post_process_rec(rec)

        # Objectify and return
        return Prediction(
            category_ids=rec["category"],
            gender=rec["gender"],
            score=rec["score"],
            liked=rec["liked"],
        )

    @staticmethod
    def _post_process_rec(dataset):
        """
        Process recommendation list: Score normalization per gender
        :param dataset ['gender', 'category', 'score', 'liked']
        :return dataset ['gender', 'category', 'score', 'liked']
        """
        dataset = dataset.copy()
        dataset = dataset.assign(log_score=lambda x: np.log1p(x.score))
        """
        For each gender 0, 1, 2
        Calculate normalized score
        then Append to the final rec_dataset
        """
        rec_dataset = pd.DataFrame()
        for gender in dataset.gender.unique():
            dataset_gender = dataset[dataset.gender == gender].copy()
            dataset_gender = RecPred._gender_processing(dataset_gender)
            rec_dataset = rec_dataset.append(dataset_gender, sort=False)

        rec_dataset = rec_dataset.sort_values(by=["score"], ascending=[False])
        rec_dataset.reset_index(inplace=False)
        rec_dataset.score = np.round(rec_dataset.score, decimals=6)

        return rec_dataset[["gender", "category", "score", "liked"]]

    """
    Normalise the scores
    """

    @staticmethod
    def _gender_processing(dataset):
        dataset = dataset.copy()
        max_score = np.max(dataset.log_score)
        dataset = dataset.assign(norm_score=lambda x: x.log_score / max_score)
        dataset.drop(columns=["score"], axis=1, inplace=True)
        dataset.rename(columns={"norm_score": "score"}, inplace=True)

        return dataset[["gender", "category", "score", "liked"]]
