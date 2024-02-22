import json
from math import nan
from copy import deepcopy
import random
import numpy as np
import scipy.stats
import math
from tqdm import tqdm
import os
from .utils import *
from .base import *
from .prompts import *


class EvaluateScalarMetaFeedback(BaseEvaluator):

    def __init__(self, flag='test', split='obj', prediction_path=[], raw_data_path=[]):
        super(EvaluateScalarMetaFeedback, self).__init__(flag=flag, split=split, prediction_path=prediction_path, raw_data_path=raw_data_path)

    def evaluate(self):
        '''calcualte the pearson and spearman scores for the samples'''
        feedback_scores = []
        generated_scores = []
        qualities = []
        error_num = 0
        for sample, item in zip(self.predictions, self.samples):
            # score = extract_decision(sample['prediction'])
            score = extract_score(sample['prediction'])
            gt_score = item['meta_feedback_score']
            if not score or score > 7:
                error_num += 1
            generated_scores.append(score)
            feedback_scores.append(float(gt_score))
            qualities.append(item['raw_quality'])
        sp = scipy.stats.spearmanr(generated_scores, feedback_scores)[0]
        meta_qualities = ['low', 'med', 'high']
        subscores = {}
        for quality, gs, gts in zip(qualities, generated_scores, feedback_scores):
            if quality not in subscores:
                subscores[quality] = {
                    'gs': [gs],
                    'gts': [gts]
                }
            else:
                subscores[quality]['gs'].append(gs)
                subscores[quality]['gts'].append(gts)
        sps = {}
        for quality in meta_qualities:
            s = scipy.stats.spearmanr(subscores[quality]['gs'], subscores[quality]['gts'])[0]
            sps[quality] = round(s*100, 2)
        return round(sp*100, 2), sps
