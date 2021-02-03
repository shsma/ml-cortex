"""
@name: metrics.py
@author: Graydon Snider, Mohammad Jeihoonian
Created on Sept 2019
"""
import numpy as np
import pandas as pd


def jaccard_ranked(actual: list, predicted: list, k):

    """
    :param actual:
    :param predicted:
    :param k:
    :return:

    note that both actual and predicted orders matter

    """

    bin_size = max(len(actual), len(predicted))
    bin_size = min(bin_size, k)

    mean_score = 0

    for i in range(1, bin_size + 1):

        s1 = set(actual[:i])
        s2 = set(predicted[:i])

        # calculate Jaccard similarity of subset lists
        score = len(s1.intersection(s2)) / len(s1.union(s2))

        mean_score += score

    return mean_score / bin_size


def jaccard_at_k(actual: list, predicted: list, k):

    """
    :param actual
    :param predicted
    :param k
    :return: mean score of jaccard distances
    """

    bin_size = max(len(actual), len(predicted))
    bin_size = min(bin_size, k)

    s1 = set(actual[:bin_size])
    s2 = set(predicted[:bin_size])

    # calculate Jaccard similarity of subset lists
    mean_score = len(s1.intersection(s2)) / len(s1.union(s2))

    return mean_score


def recall_at_k(actual, predicted, k=10):

    """
    Computes the recall at k.
    This function computes the recall at k between two lists of
    items.
    Parameters
    ----------
    actual : list
             A list of elements that are to be predicted (order doesn't matter)
    predicted : list
                A list of predicted elements (order does matter)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The recall at k over the input lists
    """
    num_hits = 0.0
    predicted = predicted[:k]

    for i, p in enumerate(predicted):
        if p in actual and p not in predicted[:i]:
            num_hits += 1.0
    if not actual or not predicted:
        return 0.0
    return num_hits / len(actual)


def avg_recall_at_k(actual, predicted, k=10):
    """
    Computes the mean recall at k.
    This function computes the mean recall at k between two lists
    of lists of items.
    Parameters
    ----------
    actual : list
             A list of lists of elements that are to be predicted
             (order doesn't matter in the lists)
    predicted : list
                A list of lists of predicted elements
                (order matters in the lists)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The mean recall at k over the input lists
    """
    return np.mean([recall_at_k(a, p, k) for a, p in zip(actual, predicted)])


def precision_at_k(actual, predicted, k=10):

    """
    Computes the recall at k.
    This function computes the precision at k between two lists of
    items.
    Parameters
    ----------
    actual : list
             A list of elements that are to be predicted (order doesn't matter)
    predicted : list
                A list of predicted elements (order does matter)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The precision at k over the input lists
    """
    num_hits = 0.0
    predicted = predicted[:k]

    for i, p in enumerate(predicted):
        if p in actual and p not in predicted[:i]:
            num_hits += 1.0
    if not actual or not predicted:
        return 0.0
    return num_hits / len(predicted)


def avg_precision_at_k(actual, predicted, k=10):
    """
    Computes the mean precision at k.
    This function computes the mean precision at k between two lists
    of lists of items.
    Parameters
    ----------
    actual : list
             A list of lists of elements that are to be predicted
             (order doesn't matter in the lists)
    predicted : list
                A list of lists of predicted elements
                (order matters in the lists)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The mean precision at k over the input lists
    """
    return np.mean([precision_at_k(a, p, k) for a, p in zip(actual, predicted)])


def f1_at_k(actual, predicted, k):

    """
    Computes the f1 at k.
    This function computes the f1 score at k between two lists of items.

    Parameters
    ----------
    actual : list
             A list of elements that are to be predicted (order doesn't matter)
    predicted : list
                A list of predicted elements (order does matter)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The precision at k over the input lists
    """

    prec = precision_at_k(actual, predicted, k)
    recall = recall_at_k(actual, predicted, k)

    try:
        f1 = 2 * prec * recall / (prec + recall)
    except (ValueError, ZeroDivisionError):
        f1 = 0

    return f1


def avg_f1_at_k(actual, predicted, k=10):
    """
    Computes the mean f1 at k.
    This function computes the mean precision at k between two lists
    of lists of items.
    Parameters
    ----------
    actual : list
             A list of lists of elements that are to be predicted
             (order doesn't matter in the lists)
    predicted : list
                A list of lists of predicted elements
                (order matters in the lists)
    k : int, optional
        The maximum number of predicted elements
    Returns
    -------
    score : double
            The mean precision at k over the input lists
    """
    return np.mean([f1_at_k(a, p, k) for a, p in zip(actual, predicted)])


def df_of_lists(dataframe: pd.DataFrame,
                target_col: str,
                group_col: list,
                agg_name: str = None):

    if agg_name is None:
        agg_name = target_col

    return dataframe.groupby(group_col)[target_col].apply(list).reset_index(name=agg_name)


def list_of_lists(dataframe: pd.DataFrame,
                  target_col: str,
                  group_col: str):

    return dataframe.groupby(group_col)[target_col].apply(list).reset_index(name='test').test.to_list()
