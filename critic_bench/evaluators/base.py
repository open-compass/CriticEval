import json
import os
import ipdb
import random
import numpy as np
import scipy.stats
from .utils import *


class BaseEvaluator():

    def __init__(self, 
        prediction_path=[], 
        raw_data_path=[],
        flag='sub',    # sub or obj
        split='test',     # test or dev
    ):
        self.flag = flag
        self.split = split
        self.prediction_path = prediction_path
        self._file_path = raw_data_path
        if flag == 'obj':
            self._load_data_obj()
        else:
            self._load_data_sub()

    def _load_data_obj(self):
        '''load all the domains'''
        assert len(self._file_path) == len(self.prediction_path)
        self.predictions = {}
        self.samples = []
        index = 0
        for file, _file in list(zip(self.prediction_path, self._file_path)):
            if os.path.exists(file) is False or os.path.exists(_file) is False:
                continue
            with open(_file) as f:
                self.samples.extend(json.load(f))
            with open(file) as f:
                predictions = json.load(f)
            for key in predictions:
                self.predictions[str(index + int(key))] = predictions[key]
            index += len(predictions)
            # print('=' * 30, f'process file:', file, _file, '=' * 30)
        self.predictions = [self.predictions[str(i)] for i in range(len(self.predictions))]
        assert len(self.predictions) == len(self.samples), f'ERROR {self.prediction_path}: The samples of prediction and raw data should be the same, but get {len(self.predictions)} predictions and {len(self.samples)} raw data samples'
        # check every item whether are aligned
        for a, b in zip(self.predictions, self.samples):
            # assert b['question'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
            if type(a['origin_prompt']) is str:
                assert b['question'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
            else:
                assert type(a['origin_prompt']) is list
                assert b['question'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
            if 'generation' in b:
                if type(a['origin_prompt']) is str:
                    assert b['generation'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
                else:
                    assert b['generation'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
            elif 'obj' in b:
                if type(a['origin_prompt']) is str:
                    assert b['obj']['generation_a'] in a['origin_prompt'][0]['prompt'] and b['obj']['generation_b'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
                else:
                    assert b['obj']['generation_a'] in a['origin_prompt'] and b['obj']['generation_b'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
            else:
                raise Exception(f'[!] Unknow critique task')
            
    def _load_data_sub(self):
        '''load each domain'''
        assert len(self._file_path) == len(self.prediction_path)
        self.predictions = []
        self.samples = []
        for file, _file in zip(self.prediction_path, self._file_path):
            if os.path.exists(file) is False or os.path.exists(_file) is False:
                print(f'[!] ignore not exist file:', file, _file)
                continue
            with open(_file) as f:
                self.samples.append(json.load(f))
            with open(file) as f:
                predictions = json.load(f)
            p = {}
            index = 0
            for key in predictions:
                p[str(index + int(key))] = predictions[key]
            index += len(predictions)
            p = [p[str(i)] for i in range(len(p))]
            self.predictions.append(p)
            assert len(self.predictions[-1]) == len(self.samples[-1]), f'ERROR {file}: The samples of prediction and raw data should be the same, but get {len(self.predictions[-1])} predictions and {len(self.samples[-1])} raw data samples'
            # check every item whether are aligned
            for a, b in zip(self.predictions[-1], self.samples[-1]):
                if type(a['origin_prompt']) is str:
                    assert b['question'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
                else:
                    assert type(a['origin_prompt']) is list
                    assert b['question'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
                if 'generation' in b:
                    if type(a['origin_prompt']) is str:
                        assert b['generation'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
                    else:
                        assert b['generation'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
                elif 'sub' in b:
                    if type(a['origin_prompt']) is str:
                        assert b['sub']['generation_a'] in a['origin_prompt'] and b['sub']['generation_b'] in a['origin_prompt'], f'Question context must in the origin_prompt generared by opencompass'
                    else:
                        assert b['sub']['generation_a'] in a['origin_prompt'][0]['prompt'] and b['sub']['generation_b'] in a['origin_prompt'][0]['prompt'], f'Question context must in the origin_prompt generared by opencompass'
                else:
                    raise Exception(f'[!] Unknow critique task')

    def evaluate(self):
        raise NotImplementedError
