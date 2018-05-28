import logging

from csrank.feta_network import FETANetwork
from csrank.losses import hinged_rank_loss
from csrank.metrics import zero_one_rank_loss_for_scores
from .object_ranker import ObjectRanker

__all__ = ['FETAObjectRanker']


class FETAObjectRanker(FETANetwork, ObjectRanker):
    def __init__(self, loss_function=hinged_rank_loss, metrics=None, **kwargs):
        if metrics is None:
            metrics = [zero_one_rank_loss_for_scores]
        super().__init__(self, metrics=metrics, loss_function=loss_function, **kwargs)
        self.logger = logging.getLogger(FETAObjectRanker.__name__)

    def fit(self, X, Y, **kwd):
        super().fit(self, X, Y, **kwd)

    def predict(self, X, **kwargs):
        return super().predict(self, X, **kwargs)

    def predict_for_scores(self, scores, **kwargs):
        ObjectRanker.predict_for_scores(self, scores, **kwargs)

    def _predict_scores_fixed(self, X, **kwargs):
        return super()._predict_scores_fixed(self, X, **kwargs)

    def predict_scores(self, X, **kwargs):
        return super().predict_scores(self, X, **kwargs)

    def clear_memory(self, **kwargs):
        self.logger.info("Clearing memory")
        FETANetwork.clear_memory(self, **kwargs)
