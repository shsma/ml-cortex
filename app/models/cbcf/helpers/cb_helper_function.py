"""
@name: brandcoldstart.py
@overview: Takes user interactions with brand genders as input and recommends top k brands as output
@author: Graydon Snider
Created on March 11, 2019
"""

# -------- generic libraries ------ #
import datetime
from datetime import datetime
import numpy as np
import pandas as pd
import re

from sklearn.preprocessing import normalize

from sklearn.feature_extraction.text import CountVectorizer
from implicit import nearest_neighbours

from gensim.parsing.preprocessing import \
    remove_stopwords, strip_numeric, strip_short, strip_non_alphanum, \
    strip_punctuation, strip_multiple_whitespaces

CB_REC_PARAM = dict(
    max_product_age_weeks=95,
    last_n_weeks_test=1,
    n_rec_male=50,
    n_rec_female=50,

    item_col_name='bg',
    quantile=0.5,

    min_df=2,
    B=0.75,
    K1=1.2,

    # table destinations
    user_score='bg_user_scores_raw.pkl',
    product_info='bg_products_raw.pkl',

    # to be deprecated
    dataset_name='ds_rec',
    cf_train_name='bg_cf_score_train',
    cf_test_name='bg_cf_score_train',
    cb_train_name='bg_cb_score_train',

    # static filenames
    bg_product_static='bg_product_evaluation.pkl',
    bg_user_static='bg_user_evaluation.pkl',

    # production filenames (rolling time window)
    bg_product_production='bg_product_production.pkl',
    bg_user_production='bg_user_production.pkl')


def _matrix_quantile_zeroes(weights_inner: pd.DataFrame,
                            quantile: float) -> pd.DataFrame:

    assert (quantile >= 0) & (quantile <= 1), 'Quantile outside range 0 <= x <= 1'

    dimension = weights_inner.shape[0]

    # get vector of quantiles
    quantile_vect = np.quantile(weights_inner, quantile, axis=0)

    # repeat vector, matching dimension of imput similaity matrix
    quantile_mat = np.repeat(quantile_vect, dimension, axis=0).reshape(dimension, dimension)

    # note that similarity quantiles are set to columns-wise
    # (ie each column (not row) contains the top K most similar results
    tf = weights_inner < quantile_mat.T

    # set values below threshold to zero
    weights_inner[tf] = 0

    return weights_inner


def get_text_distance(corpus_in: list,
                      stock_in: list,
                      docids_in: list) -> pd.DataFrame:
    """
    :param corpus_in:
    :param stock_in:
    :param docids_in:
    :return weights_inner_pd: pandas dataframe and top 5 similar brand csv file
    """

    vectorize = CountVectorizer(min_df=CB_REC_PARAM['min_df'])
    X = vectorize.fit_transform(corpus_in)  # X is a sparse matrix
    weights = nearest_neighbours.bm25_weight(X=X, K1=CB_REC_PARAM['K1'], B=CB_REC_PARAM['B']).toarray()

    # normalize, make symmetric matrix inner product
    weights_norm = normalize(weights, axis=1, norm='l2')
    weights_inner = weights_norm @ weights_norm.T

    # ----------- modify results using stock level -------------- #
    stock_level = np.array(stock_in)
    stock_level[stock_level > 0] = 1
    stock_level[stock_level <= 0] = 0

    stock_diagonal = np.diag(stock_level)

    weights_relevance_score = weights_inner @ stock_diagonal
    # weights_relevance_score = np.multiply(weights_inner, stock_level)

    balance = 3
    weights_relevance_score = weights_relevance_score / balance + stock_diagonal * (1 - 1 / balance)

    weights_relevance_score = weights_relevance_score.round(decimals=5)

    # ---------- return pandas dataframe -------- #

    # convert matrix to dataframe
    ROWS = pd.Index(docids_in, name="rows")
    COLS = pd.Index(docids_in, name="cols")

    # reindex contains the missing columns
    weights_inner_pd = pd.DataFrame(weights_relevance_score,
                                    index=ROWS,
                                    columns=COLS)

    weights_inner_pd = _matrix_quantile_zeroes(weights_inner_pd, quantile=CB_REC_PARAM['quantile'])

    return weights_inner_pd


def clean_text(x: str) -> str:
    """
    :param x: raw string
    :return x: cleaned string
    """

    x = x.lower()
    x = re.sub('ssense|exclusive', '', x)

    x = strip_non_alphanum(x)
    x = strip_numeric(x)
    x = strip_short(x, minsize=2)
    x = remove_stopwords(x)
    x = strip_punctuation(x)
    x = strip_multiple_whitespaces(x)

    return x


def merge_description(df, col_list_in):
    return df[col_list_in].apply(lambda y: clean_text(' '.join(y)), axis=1)


def cb_manipulate_text(raw_text_in: pd.DataFrame,
                       start_date: str,
                       end_date: str):
    """
    :param raw_text_in: unprocessed product dataframe
    :param start_date: str
    :param end_date: str
    :return:
    """

    date_min = datetime.strptime(start_date, "%Y-%m-%d")
    date_max = datetime.strptime(end_date, "%Y-%m-%d")

    assert date_min <= date_max, 'Error: start date must be less than end date'

    raw_text_in.rename(columns={'prodCreationDate': 'creationDate'}, inplace=True)

    raw_text_in = (raw_text_in.assign(gender=lambda x: np.where(x.gender == 'women', '0',
                                                                np.where(x.gender == 'men', '1', '2')),
                                      b_g=lambda x: x['brandID'].astype(str) + ' ' + x['gender'].astype(str)))

    # define four price groups (repeat word twice)
    raw_text_in['priceCDtxt'] = 'pricePrem pricePrem priceHigh'
    raw_text_in.loc[raw_text_in['priceCD'].between(0, 300, inclusive=False), 'priceCDtxt'] = 'priceLow priceLow'
    raw_text_in.loc[raw_text_in['priceCD'].between(300, 600, inclusive=True), 'priceCDtxt'] = 'priceMed priceMed'
    raw_text_in.loc[raw_text_in['priceCD'].between(600, 1000, inclusive=True), 'priceCDtxt'] = 'priceHigh priceHigh'

    # adjust descriptions
    raw_text_in['firstW'] = raw_text_in.name.str.split(' |_').str[0]
    raw_text_in = raw_text_in[~raw_text_in['description'].isnull()]
    raw_text_in['description'] = raw_text_in['description'].apply(lambda x: strip_non_alphanum(x))
    raw_text_in_list = raw_text_in.description.str.split(' ')
    raw_text_in['fitSize'] = raw_text_in_list.str[0] + ' ' + raw_text_in_list.str[1]

    # frequency of repeated products
    col_list_rep = {'name': 1,
                    'firstW': 1,  # color
                    'fitSize': 2,  # 2
                    'description': 1,
                    'composition': 1,
                    'priceCDtxt': 2,
                    'subcategory': 1}

    # duplicate words n times from dictionary
    for key, value in col_list_rep.items():
        if value > 1:
            raw_text_in[key] = (raw_text_in[key] + " ") * value

    # choose which columns to join together
    col_list = ['description', 'composition', 'category', 'name']

    # data pre-processing
    raw_text_gend = (raw_text_in
                     .assign(creationDate=lambda x: pd.to_datetime(x['creationDate']),
                             creationDateMax=lambda x: x.groupby(['b_g'])['creationDate'].transform(max))
                     .pipe(lambda x: x[x['creationDate'] <= date_max])
                     .pipe(lambda x: x[(x['creationDate'] > date_min) | (x['creationDateMax'] < date_min)])
                     .assign(description=lambda x: merge_description(x.astype(str), col_list_in=col_list))
                     )

    # merge all brand information together
    collapse_brands = {'description': [lambda x: ' '.join(x)],
                       'stockForSale': ['sum'],
                       'creationDateMax': ['max'],
                       }

    bg_text = (raw_text_gend[['b_g', 'brandID', 'gender', 'description', 'stockForSale', 'creationDateMax']]
               .groupby(['b_g', 'brandID', 'gender'], as_index=False)
               .agg(collapse_brands))

    # flatten agg column labels into one row
    mi = bg_text.columns.tolist()
    flat_ind = pd.Index([e[0] for e in mi])
    bg_text.columns = flat_ind

    bg_text = bg_text.astype({'b_g': 'category'})

    return bg_text
