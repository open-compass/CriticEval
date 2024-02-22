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


class EvaluateScalarFeedback(BaseEvaluator):

    def __init__(self, flag='test', split='obj', prediction_path=[], raw_data_path=[]):
        super(EvaluateScalarFeedback, self).__init__(flag=flag, split=split, prediction_path=prediction_path, raw_data_path=raw_data_path)

    def evaluate(self):
        '''calcualte the pearson and spearman scores for the samples'''
        feedback_scores = []
        generated_scores = []
        qualities = []
        error_num = 0
        for sample, item in zip(self.predictions, self.samples):
            score = extract_decision(sample['prediction'])
            gt_score = item['feedback_score']
            if not score or score > 7:
                error_num += 1
            generated_scores.append(score)
            feedback_scores.append(float(gt_score))
            qualities.append(item['metadata']['quality'])
        sp = scipy.stats.spearmanr(generated_scores, feedback_scores)[0]
        meta_qualities = ['low', 'med', 'high', 'super-high']
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
        if 'super-high' not in subscores:
            meta_qualities.remove('super-high')
        for quality in meta_qualities:
            s = scipy.stats.spearmanr(subscores[quality]['gs'], subscores[quality]['gts'])[0]
            sps[quality] = round(s*100, 2)
        return round(sp*100, 2), sps

class EvaluateNLFeedback(BaseEvaluator):

    '''Evaluate the feedback performence by the powerful LLM, like GPT-4
    include the reference feedback to evaluate
    '''

    def __init__(self, flag='test', split='sub', prediction_path=[], raw_data_path=[], evaluation_path=[], domain_names=[], fast_mode=False):
        super(EvaluateNLFeedback, self).__init__(flag=flag, split=split, prediction_path=prediction_path, raw_data_path=raw_data_path)
        self.evaluation_path = evaluation_path
        self.domain_names = domain_names
        self.fast_mode = fast_mode
        self.backup_nums = []
        for file in self.evaluation_path:
            if os.path.exists(file):
                backup_num = len([line for line in open(file).readlines() if line.strip()])
            else:
                backup_num = 0
            self.backup_nums.append(backup_num)
        # prediction, samples are a list of list, saving results from each file
        try:
            assert len(self.evaluation_path) == len(self._file_path) == len(self.prediction_path) == len(self.predictions) == len(self.samples) == len(self.domain_names)
            self.valid = True
        except:
            self.valid = False

    def batch_evaluate(self, batch_size=8):
        collector_s, collector_sps = {}, {}
        for evaluate_save_path, predictions, samples, backup_num, domain_name in tqdm(list(zip(self.evaluation_path, self.predictions, self.samples, self.backup_nums, self.domain_names))):
            scores, subscores = self._batch_evaluate(evaluate_save_path, predictions, samples, backup_num, domain_name, batch_size=batch_size)
            if domain_name not in collector_s:
                collector_s[domain_name] = scores
                collector_sps[domain_name] = subscores
            else:
                collector_s[domain_name].extend(scores)
                for q in subscores:
                    if q not in collector_sps[domain_name]:
                        collector_sps[domain_name][q] = subscores[q]
                    else:
                        collector_sps[domain_name][q].extend(subscores[q])
        # generate the score summarization
        final_rest, final_subscore_rest = {}, {}
        for _domain_name in collector_s:
            final_rest[_domain_name] = round(np.mean(collector_s[_domain_name]), 2)
            final_subscore_rest[_domain_name] = {key: round(np.mean(collector_sps[_domain_name][key]), 2) for key in collector_sps[_domain_name]}
        return final_rest, final_subscore_rest

    def _batch_evaluate(self, evaluate_save_path, predictions, samples_, backup_num, domain_name, batch_size=8):
        '''Inference one file'''
        if self.fast_mode is False:
            with open(evaluate_save_path, 'a') as f:
                pbar = tqdm(total=len(predictions))
                pbar.update(backup_num)
                cache, samples = [], []
                for item, sample in list(zip(predictions[backup_num:], samples_[backup_num:])):
                    if domain_name == 'code_exec':
                        content = code_exec_feedback_prompt.format(**{
                            'q': sample['question'], 
                            'ut': sample['unit_test'], 
                            'r': sample['generation'], 
                            'exec_rest': sample['exec_rest'],
                            'f_a': sample['feedback'],
                            'f_b': item['prediction'],
                        })
                    elif domain_name == 'code_not_exec':
                        content = code_not_exec_feedback_prompt.format(**{
                            'q': sample['question'], 
                            'ut': sample['unit_test'], 
                            'r': sample['generation'],
                            'f_a': sample['feedback'],
                            'f_b': item['prediction'],
                        })
                    elif domain_name in ['translate']:
                        content = translate_feedback_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['chat']:
                        content = chat_feedback_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['qa']:
                        content = qa_feedback_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['harmlessness']:
                        content = harmlessness_feedback_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['math_cot']:
                        content = math_cot_feedback_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['math_pot']:
                        content = math_pot_feedback_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name == 'summary':
                        content = summary_feedback_prompt.format(
                            a=sample['article'],
                            q=sample['question'],
                            r=sample['generation'],
                            f_a=sample['feedback'],
                            f_b=item['prediction'],
                        )
                    cache.append(content)
                    samples.append(deepcopy(sample))
                    if len(cache) % batch_size == 0:
                        rests = batch_chat([{
                            'model': 'gpt-4-1106-preview',
                            'messages': [
                                {
                                    'role': 'user',
                                    'content': i
                                }    
                            ],
                        } for i in cache], temp=0.0)
                        for rest, new_item in zip(rests, samples):
                            score = extract_decision(rest)
                            new_item['evaluation'] = {
                                'cot': rest,
                                'score': score
                            }
                            f.write(json.dumps(new_item, ensure_ascii=False) + '\n')
                            f.flush()
                        cache = []
                        samples = []
                        pbar.update(batch_size)
                if len(cache) > 0:
                    rests = batch_chat([{
                        'model': 'gpt-4-1106-preview',
                        'messages': [
                            {
                                'role': 'user',
                                'content': i
                            }    
                        ],
                    } for i in cache], temp=0.0)
                    for rest, new_item in zip(rests, samples):
                        score = extract_decision(rest)
                        new_item['evaluation'] = {
                            'cot': rest,
                            'score': score
                        }
                        f.write(json.dumps(new_item, ensure_ascii=False) + '\n')
                        f.flush()
                    pbar.update(len(cache))
                    cache = []
                    samples = []

        # read file and get the evaluation results
        try:
            with open(evaluate_save_path) as f:
                scores = []
                error_counter = 0
                subscores = {}
                for line in f.readlines():
                    item = json.loads(line)
                    score = item['evaluation']['score']
                    if item['evaluation']['cot'] is None or 'Bad gateway' in item['evaluation']['cot'] or not score or score > 10:
                        error_counter += 1
                        continue
                    scores.append(score)
                    quality = item['metadata']['quality']
                    if quality not in subscores:
                        subscores[quality] = [score]
                    else:
                        subscores[quality].append(score)
                for q in ['low', 'med', 'high', 'super-high']:
                    if q not in subscores:
                        subscores[q] = []
        except Exception as error:
            print('Meet error:', error)
            scores, subscores = [], {'low': [], 'med': [], 'high': [], 'super-high': []}
        return scores, subscores

