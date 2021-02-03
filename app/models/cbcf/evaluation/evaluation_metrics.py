"""
@name: evaluation_metric.py
@author: Graydon Snider
Created on Sept 2019
"""
from app.models.cbcf.helpers.metrics import *


class EvaluationMetrics(object):

    # load in dataframe and the metrics you want to implement
    def __init__(self, actual: list, predict: list, k_val: int):

        assert isinstance(k_val, int), "k must be an integer"

        # 'actual' and 'predict' should be a list of lists
        self.actual = actual
        self.predict = predict
        self.k_val = k_val

    def grouping_score_ranked(self):

        methods = {'jaccard_ranked': jaccard_ranked,
                   'jaccard_at_k': jaccard_at_k,
                   'recall_at_k': recall_at_k,
                   'precision_at_k': precision_at_k,
                   'f1_at_k': f1_at_k}

        metrics = dict()

        metrics['k_value'] = self.k_val

        for key in methods:

            # aggregate on the specific metric
            metric = [methods.get(key)(a, p, self.k_val) for a, p in zip(self.actual, self.predict)]

            metrics[key] = f'mean: {np.round(np.mean(metric), 4)}, std: {np.round(np.std(metric),4)}'

        # additional meta metrics

        metrics['member_gender_count'] = len(self.actual)
        metrics['mean_length_true'] = np.round(np.mean([len(x) for x in self.actual]), 2)
        metrics['mean_length_predict'] = np.round(np.mean([len(x[:self.k_val]) for x in self.predict]), 0)

        return metrics
