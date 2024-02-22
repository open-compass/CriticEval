from .base import *
from copy import deepcopy
from math import nan
from .utils import *
from .prompts import *
import os
from tqdm import tqdm
import ipdb


class EvaluateMathCorrection(BaseEvaluator):

    def __init__(self, prediction_path=[], raw_data_path=[], split='test', flag='obj', dataset_name='math_cot'):
        super(EvaluateMathCorrection, self).__init__(prediction_path=prediction_path, raw_data_path=raw_data_path, split=split, flag=flag)
        self.dataset_name=dataset_name

    def _evaluate_math_cot_correction(self):
        results = []
        error_num = 0
        qualities = []
        for index, (sample, item) in tqdm(list(enumerate(zip(self.predictions, self.samples)))):
            rest = parse_math_result(sample['prediction'])
            gt_rest = parse_math_result(item['ground_truth_answer'])
            qualities.append(item['metadata']['quality'])
            if not rest:
                results.append(0)
                error_num += 1
                continue
            else:
                if rest == gt_rest:
                    results.append(1)
                else:
                    results.append(0)
        assert len(results) == len(qualities)
        return results, qualities

    def _evaluate_math_pot_correction(self):
        results = []
        error_num = 0
        qualities = []
        for index, (sample, item) in tqdm(list(enumerate(zip(self.predictions, self.samples)))):
            try:
                code = parse_code(sample['prediction'])
            except:
                error_num += 1
                results.append(0)
                continue
            qualities.append(item['metadata']['quality'])
            if not code:
                error_num += 1
                results.append(0)
                continue
            exec_rest = exec_math_code(code, uts=[{'input': '', 'output': parse_math_result(item['ground_truth_answer'])}])
            if exec_rest['status'] == 'PASSED':
                results.append(1)
            else:
                results.append(0)
        return results, qualities

    def evaluate(self):
        if self.dataset_name == 'math_cot':
            results, qualities = self._evaluate_math_cot_correction()
        else:
            results, qualities = self._evaluate_math_pot_correction()
        sss_ = round(np.mean(results)*100, 2)
        # different qualities
        meta_qualities = ['low', 'med', 'high']
        subscores = {'low': [], 'med': [], 'high': []}
        for quality, r in zip(qualities, results):
            subscores[quality].append(r)
        sps = {'low': 0, 'med': 0, 'high': 0}
        for q in meta_qualities:
            sps[q] = round(np.mean(subscores[q])*100, 2)
        return sss_, sps


class EvaluateCodeCorrection(BaseEvaluator):

    '''Compute the results on the Math questions and get the results (With execution)'''

    def __init__(self, prediction_path=[], raw_data_path=[], split='test', flag='obj', dataset_name='code_exec'):
        super(EvaluateCodeCorrection, self).__init__(prediction_path=prediction_path, raw_data_path=raw_data_path, split=split, flag=flag)
        self.dataset_name = dataset_name

    def evaluate(self):
        accuracy = []
        error_num = 0
        qualities = []
        for index, (sample, item) in tqdm(list(enumerate(zip(self.predictions, self.samples)))):
            qualities.append(item['metadata']['quality'])
            try:
                code = parse_code(sample['prediction'])
            except:
                print('==========', 'strange error', '==========')
                accuracy.append(0)
                error_num += 1
                continue
            if not code:
                accuracy.append(0)
                error_num += 1
                continue
            code = code + item["unit_test"]
            if item['data_source'] == 'humaneval':
                function_name = find_fist_function_name(code)
                code += f'\ncheck({function_name})'
            exec_rest = exec_code_no_unit_test(code)
            if exec_rest['status'] == 'PASSED':
                accuracy.append(1)
            else:
                accuracy.append(0)
        meta_qualities = ['low', 'med', 'high']
        subscores = {'low': [], 'med': [], 'high': []}
        for quality, r in zip(qualities, accuracy):
            subscores[quality].append(r)
        sps = {'low': 0, 'med': 0, 'high': 0}
        for q in meta_qualities:
            sps[q] = round(np.mean(subscores[q])*100, 2)
        return round(np.mean(accuracy)*100, 2), sps


class EvaluateNLCorrection(BaseEvaluator):

    def __init__(self, flag='test', split='sub', prediction_path=[], raw_data_path=[], evaluation_path=[], domain_names=[], fast_mode=False):
        super(EvaluateNLCorrection, self).__init__(flag=flag, split=split, prediction_path=prediction_path, raw_data_path=raw_data_path)
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
        if self.fast_mode is False:
            pbar = tqdm(total=len(predictions))
            pbar.update(backup_num)
            with open(evaluate_save_path, 'a') as f:
                cache = []
                samples = []
                for item, sample in list(zip(predictions[backup_num:], samples_[backup_num:])):
                    if domain_name in ['translate']:
                        content = translate_correction_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f=sample['feedback'],
                            c_a=sample['correction'],
                            c_b=item['prediction'],
                        )
                    elif domain_name in ['chat']:
                        content = chat_correction_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f=sample['feedback'],
                            c_a=sample['correction'],
                            c_b=item['prediction'],
                        )
                    elif domain_name in ['qa']:
                        content = qa_correction_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f=sample['feedback'],
                            c_a=sample['correction'],
                            c_b=item['prediction'],
                        )
                    elif domain_name in ['harmlessness']:
                        content = harmlessness_correction_prompt.format(
                            q=sample['question'],
                            r=sample['generation'],
                            f=sample['feedback'],
                            c_a=sample['correction'],
                            c_b=item['prediction'],
                        )
                    elif domain_name == 'summary':
                        content = summary_correction_prompt.format(
                            a=sample['article'],
                            q=sample['question'],
                            r=sample['generation'],
                            f=sample['feedback'],
                            c_a=sample['correction'],
                            c_b=item['prediction'],
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
                        samples = []
                        cache = []
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
                    samples = []
                    cache = []
                    pbar.update(len(cache))

        try:
            with open(evaluate_save_path) as f:
                scores = []
                error_counter = 0
                subscores = {}
                for line in f.readlines():
                    item = json.loads(line)
                    try:
                        score = item['evaluation']['score']
                        if 'Bad gateway' in item['evaluation']['cot'] or 'Bad Gateway' in item['evaluation']['cot'] or not score or score > 10:
                            error_counter += 1
                            continue
                    except:
                        print(f'[!] no score found')
                        continue
                    scores.append(score)
                    quality = item['metadata']['quality']
                    if quality not in subscores:
                        subscores[quality] = [score]
                    else:
                        subscores[quality].append(score)
                for q in ['low', 'med', 'high']:
                    if q not in subscores:
                        subscores[q] = []
        except Exception as error:
            print('Meet error:', error)
            scores, subscores = [], {'low': [], 'med': [], 'high': []}
        return scores, subscores
