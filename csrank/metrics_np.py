from functools import partial
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
    zero_one_loss,
    hamming_loss,
)

from csrank.numpy_util import scores_to_rankings

__all__ = [
    "spearman_correlation_for_scores_np",
    "kendalls_tau_for_scores_np",
    "zero_one_accuracy_for_scores_np",
    "zero_one_rank_loss_for_scores_ties_np",
    "zero_one_accuracy_np",
    "zero_one_rank_loss_for_scores_np",
    "auc_score",
    "instance_informedness",
    "f1_measure",
    "recall",
    "hamming",
    "average_precision",
    "precision",
    "subset_01_loss",
    "spearman_correlation_for_scores_scipy",
    "topk_categorical_accuracy_np",
    "categorical_accuracy_np",
    "make_ndcg_at_k_loss_np",
]


def spearman_correlation_for_scores_np(y_true, s_pred):
    y_pred = scores_to_rankings(s_pred)
    rho = []
    n_objects = y_true.shape[1]
    denominator = n_objects * (n_objects ** 2 - 1)

    for r1, r2 in zip(y_true, y_pred):
        if len(np.unique(r2)) == len(r2):
            s = 1 - (6 * np.sum((r1 - r2) ** 2) / denominator)
            rho.append(s)
        else:
            rho.append(np.nan)
    return np.nanmean(np.array(rho))


def spearman_correlation_for_scores_scipy(y_true, s_pred):
    y_pred = scores_to_rankings(s_pred)
    rho = []
    for r1, r2 in zip(y_true, y_pred):
        s = spearmanr(r1, r2)[0]
        rho.append(s)
    return np.nanmean(np.array(rho))


def kendalls_tau_for_scores_np(y_true, s_pred):
    return 1.0 - 2.0 * zero_one_rank_loss_for_scores_ties_np(y_true, s_pred)


def zero_one_accuracy_for_scores_np(y_true, s_pred):
    y_pred = scores_to_rankings(s_pred)
    acc = np.sum(np.all(np.equal(y_true, y_pred), axis=1)) / y_pred.shape[0]
    return acc


def zero_one_accuracy_np(y_true, y_pred):
    acc = np.sum(np.all(np.equal(y_true, y_pred), axis=1)) / y_pred.shape[0]
    return acc


def make_ndcg_at_k_loss_np(k=5):
    def ndcg(y_true, y_pred):
        n_instances, n_objects = y_true.shape
        relevance = np.power(2.0, ((n_objects - y_true) * 60) / n_objects) - 1.0
        relevance_pred = np.power(2.0, ((n_objects - y_pred) * 60) / n_objects) - 1.0

        log_term = np.log(np.arange(k, dtype="float32") + 2.0) / np.log(2.0)

        # Calculate ideal dcg:
        top_t = np.argsort(relevance, axis=1)[:, ::-1][:, :k]
        toprel = relevance[np.arange(n_instances)[:, None], top_t]
        idcg = np.sum(toprel / log_term, axis=-1, keepdims=True)

        # Calculate actual dcg:
        top_p = np.argsort(relevance_pred, axis=1)[:, ::-1][:, :k]
        pred_rel = relevance[np.arange(n_instances)[:, None], top_p]
        pred_rel = np.sum(pred_rel / log_term, axis=-1, keepdims=True)
        gain = pred_rel / idcg
        return gain

    return ndcg


def zero_one_rank_loss_for_scores_ties_np(y_true, s_pred):
    n_objects = y_true.shape[1]
    mask = np.greater(y_true[:, None] - y_true[:, :, None], 0).astype(float)
    mask2 = np.greater(s_pred[:, None] - s_pred[:, :, None], 0).astype(float)
    mask3 = np.equal(s_pred[:, None] - s_pred[:, :, None], 0).astype(float)

    # Calculate Transpositions
    transpositions = np.logical_and(mask, mask2)
    x = (np.sum(mask3, axis=(1, 2)) - n_objects).astype(float) / 4.0
    transpositions = np.sum(transpositions, axis=(1, 2)).astype(float)
    transpositions += x

    denominator = n_objects * (n_objects - 1.0) / 2.0
    result = transpositions / denominator
    return np.mean(result)


def zero_one_rank_loss_for_scores_np(y_true, s_pred):
    return zero_one_rank_loss_for_scores_ties_np(y_true, s_pred)


def auc_score(y_true, s_pred):
    idx = np.where(
        (y_true.sum(axis=1) != y_true.shape[-1] - 1)
        & (y_true.sum(axis=1) != y_true.shape[-1])
        & (y_true.sum(axis=1) != 1)
        & (y_true.sum(axis=1) != 0)
    )[0]
    if len(idx) > 1:
        auc = roc_auc_score(y_true[idx], s_pred[idx], average="samples")
    elif len(idx) == 1:
        auc = roc_auc_score(y_true[idx][0], s_pred[idx][0])
    else:
        auc = np.nan
    return auc


def average_precision(y_true, s_pred):
    return average_precision_score(y_true, s_pred, average="samples")


def instance_informedness(y_true, y_pred):
    tp = np.logical_and(y_true, y_pred).sum(axis=1)
    tn = np.logical_and(np.logical_not(y_true), np.logical_not(y_pred)).sum(axis=1)
    cp = y_true.sum(axis=1)
    cn = np.logical_not(y_true).sum(axis=1)
    return np.nanmean(tp / cp + tn / cn - 1)


def f1_measure(y_true, y_pred):
    return f1_score(y_true, y_pred, average="samples")


def precision(y_true, y_pred):
    return precision_score(y_true, y_pred, average="samples")


def recall(y_true, y_pred):
    return recall_score(y_true, y_pred, average="samples")


def subset_01_loss(y_true, y_pred):
    return zero_one_loss(y_true, y_pred)


def hamming(y_true, y_pred):
    return hamming_loss(y_true, y_pred)


def topk_categorical_accuracy_np(k=5):
    def topk_acc(y_true, y_pred):
        topK = y_pred.argsort(axis=1)[:, -k:][:, ::-1]
        accuracies = np.zeros_like(y_true, dtype=bool)
        y_true = np.argmax(y_true, axis=1)
        for i, top in enumerate(topK):
            accuracies[i] = y_true[i] in top
        return np.mean(accuracies)

    return topk_acc


def categorical_accuracy_np(y_true, y_pred):
    y_true = np.argmax(y_true, axis=1)
    choices = np.argmax(y_pred, axis=1)
    accuracies = np.equal(y_true, choices)
    return np.mean(accuracies)


def relevance_gain_np(grading, max_grade):
    """Plain python version of `relevance_gain`, see the documentation
    of that function for details."""
    inverse_grading = -grading + max_grade
    return (2 ** inverse_grading - 1) / (2 ** max_grade)


def err_np(y_true, y_pred, utility_function=None, probability_mapping=None):
    """Plain python version of `err`, see the documentation of that
    function for details.
    """
    if probability_mapping is None:
        # assume y_true is a ranking, use relevance gain
        max_grade = np.max(y_true)
        probability_mapping = partial(relevance_gain_np, max_grade=max_grade)
    if utility_function is None:
        # reciprocal rank
        utility_function = lambda r: 1 / r

    ninstances, nobjects = np.shape(y_pred)

    satisfied_probs = np.reshape(
        list(map(probability_mapping, y_true.flatten())), np.shape(y_true)
    )

    # sort satisfied probabilities according to the predicted ranking
    # black magic invocation to reorder each row
    row_indices = np.arange(ninstances).reshape(-1, 1)
    satisfied_at_rank = satisfied_probs[row_indices, y_pred]

    # still not satisfied after having examined the first r ranks
    not_yet_satisfied_at_rank = np.cumprod(1 - satisfied_at_rank, axis=1)

    # append a column of 1s and drop the last column, since the
    # probability the need has not been satisfied at the 0th rank is 1
    not_yet_satisfied_at_rank = np.hstack(
        (
            np.ones(np.shape(not_yet_satisfied_at_rank)[0]).reshape(-1, 1),
            not_yet_satisfied_at_rank,
        )
    )[:, :-1]

    # map over flattened array, then restore shape
    utilities = list(map(utility_function, range(1, nobjects + 1)))

    discount_at_rank = not_yet_satisfied_at_rank * utilities
    discounted_document_values = satisfied_at_rank * discount_at_rank
    results = np.sum(discounted_document_values, axis=1)
    return np.average(results)
