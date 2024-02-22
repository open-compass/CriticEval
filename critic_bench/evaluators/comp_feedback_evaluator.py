import json
from copy import deepcopy
from math import nan
import random
import numpy as np
import scipy.stats
from tqdm import tqdm
import os
from .utils import *
from .base import *
from .prompts import *


class EvaluateScalarCompFeedback(BaseEvaluator):

    def __init__(self, raw_data_path=[], prediction_path=[], reverse_prediction_path=[], split='test', flag='obj'):
        super(EvaluateScalarCompFeedback, self).__init__(raw_data_path=raw_data_path, prediction_path=prediction_path, split=split, flag=flag)

    def _load_data_obj(self):
        self.predictions, self.reverse_predictions = {}, {}
        index = 0
        self.reverse_prediction_path = [i.replace('_obj.json', '_obj_reverse.json') for i in self.prediction_path]
        self.samples = []
        assert len(self.reverse_prediction_path) == len(self.prediction_path) == len(self._file_path)
        for file_a, file_b, file_c in zip(self.reverse_prediction_path, self.prediction_path, self._file_path):
            if os.path.exists(file_a) is False or os.path.exists(file_b) is False or os.path.exists(file_c) is False:
                continue
            with open(file_a) as f:
                predictions = json.load(f)
            for key in predictions:
                self.reverse_predictions[str(index + int(key))] = predictions[key]
            #
            with open(file_b) as f:
                predictions = json.load(f)
            for key in predictions:
                self.predictions[str(index + int(key))] = predictions[key]
            #
            with open(file_c) as f:
                self.samples.extend(json.load(f))
            index += len(predictions)
        self.predictions = [self.predictions[str(i)] for i in range(len(self.predictions))]
        self.reverse_predictions = [self.reverse_predictions[str(i)] for i in range(len(self.reverse_predictions))]
        assert len(self.predictions) == len(self.samples) == len(self.reverse_predictions)
        # check every item whether are aligned
        for a, b, c in zip(self.predictions, self.reverse_predictions, self.samples):
            try:
                if type(a['origin_prompt']) == str:
                    assert c['question'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
                else:
                    assert c['question'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
            except:
                ipdb.set_trace()
            if type(b['origin_prompt']) == str:
                assert c['question'] in b['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
            else:
                assert c['question'] in b['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'

    def evaluate(self):
        '''calcualte the pearson and spearman scores for the samples'''
        accuracy = []
        qualities = []
        error_num = 0
        for sample_forward, sample_reverse, item in zip(self.predictions, self.reverse_predictions, self.samples):
            score_forward = extract_decision_option(sample_forward['prediction'])
            score_reverse = extract_decision_option(sample_reverse['prediction'])
            qs = frozenset([item['metadata']['quality_a_sub'], item['metadata']['quality_b_sub']])
            if qs == frozenset(['low', 'high']):
                qualities.append('easy')
            else:
                qualities.append('hard')

            if (not score_forward) or len(score_forward) == 0 or len(score_reverse) == 0:
                accuracy.append(0)
                continue
            if score_forward[0] not in 'ABC' or score_reverse[0] not in 'ABC':
                accuracy.append(0)
                continue
            if score_forward[0] in 'ABC' and score_reverse[0] in 'ABC' and score_forward[0] == score_reverse[0]:
                accuracy.append(0)
                continue
            gt_score = item['obj']['preference']
            if score_forward[0] == gt_score[-1]:
                accuracy.append(1)
            else:
                accuracy.append(0)

        subscores = {'easy': [], 'hard': []}
        for quality, r in zip(qualities, accuracy):
            if quality in subscores:
                subscores[quality].append(r)
        sps = {key:0 for key in subscores}
        for q in subscores:
            sps[q] = round(np.mean(subscores[q]) * 100, 2)
        return round(np.mean(accuracy)*100, 2), sps


class EvaluateNLCompFeedback(BaseEvaluator):
    
    def __init__(self, flag='test', split='sub', prediction_path=[], raw_data_path=[], evaluation_path=[], domain_names=[], fast_mode=False):
        super(EvaluateNLCompFeedback, self).__init__(flag=flag, split=split, prediction_path=prediction_path, raw_data_path=raw_data_path)
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
        print(f'[!] load {backup_num} backup subjective evaluation samples')
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
        if self.fast_mode is False:
            with open(evaluate_save_path, 'a') as f:
                pbar = tqdm(total=len(predictions))
                pbar.update(backup_num)
                cache, samples = [], []
                for item, sample in zip(predictions[backup_num:], samples_[backup_num:]):
                    if domain_name == 'code_exec':
                        if type(sample['sub']['exec_rest_a']) == str:
                            exec_rest_a = sample['sub']['exec_rest_a']
                        elif type(sample['sub']['exec_rest_a']) == dict:
                            exec_rest_a = sample['sub']['exec_rest_a']['detail']
                        else:
                            ipdb.set_trace()
                        if type(sample['sub']['exec_rest_b']) == str:
                            exec_rest_b = sample['sub']['exec_rest_b']
                        elif type(sample['sub']['exec_rest_b']) == dict:
                            exec_rest_b = sample['sub']['exec_rest_b']['detail']
                        else:
                            ipdb.set_trace()
                        content = code_exec_comp_feedback_prompt.format(**{
                            'q': sample['question'], 
                            'ut': sample['unit_test'], 
                            'r_a': sample['sub']['generation_a'], 
                            'r_b': sample['sub']['generation_b'], 
                            'exec_rest_a': exec_rest_a,
                            'exec_rest_b': exec_rest_b,
                            'f_a': sample['sub']['feedback'],
                            'f_b': item['prediction'],
                        })
                    elif domain_name == 'code_not_exec':
                        content = code_not_exec_comp_feedback_prompt.format(**{
                            'q': sample['question'], 
                            'ut': sample['unit_test'], 
                            'r_a': sample['sub']['generation_a'], 
                            'r_b': sample['sub']['generation_b'],
                            'f_a': sample['sub']['feedback'],
                            'f_b': item['prediction'],
                        })
                    elif domain_name in ['chat']:
                        content = chat_comp_feedback_prompt.format(
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['qa']:
                        content = qa_comp_feedback_prompt.format(
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['harmlessness']:
                        content = harmlessness_comp_feedback_prompt.format(
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['translate']:
                        content = translate_comp_feedback_prompt.format(
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['math_cot']:
                        content = math_cot_comp_feedback_prompt.format(
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name in ['math_pot']:
                        content = math_pot_comp_feedback_prompt.format(
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
                            f_b=item['prediction'],
                        )
                    elif domain_name == 'summary':
                        content = summary_comp_feedback_prompt.format(
                            a=sample['article'],
                            q=sample['question'],
                            r_a=sample['sub']['generation_a'],
                            r_b=sample['sub']['generation_b'],
                            f_a=sample['sub']['feedback'],
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
                        cache, samples = [], []
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
                    cache, samples = [], []
                    pbar.update(len(cache))

        try:
            with open(evaluate_save_path) as f:
                scores = []
                error_counter = 0
                subscores = {}
                meta_qualities = ['easy', 'hard']
                for line in f.readlines():
                    item = json.loads(line)
                    score = item['evaluation']['score']
                    if 'Bad gateway' in item['evaluation']['cot'] or not score or score > 10:
                        error_counter += 1
                        continue
                    scores.append(score)

                    # scores with different qualities
                    qs = frozenset([item['metadata']['quality_a_sub'], item['metadata']['quality_b_sub']])
                    if qs == frozenset(['low', 'high']):
                        qs = 'easy'
                    else:
                        qs = 'hard'
                    if qs not in subscores:
                        subscores[qs] = [score]
                    else:
                        subscores[qs].append(score)
                for q in ['easy', 'hard']:
                    if q not in subscores:
                        subscores[q] = []
        except Exception as error:
            print('Meet error:', error)
            scores, subscores = [], {'easy': [], 'hard': []}
        return scores, subscores
