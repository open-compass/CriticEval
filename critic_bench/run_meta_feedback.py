from evaluators import *
from tabulate import tabulate
from copy import deepcopy
import ipdb
import argparse
import os


def parser_args():
    parser = argparse.ArgumentParser(description='train parameters')
    parser.add_argument('--root_dir', type=str)
    parser.add_argument('--prediction_dir', type=str)
    parser.add_argument('--evaluation_dir', type=str)
    parser.add_argument('--split', type=str)
    parser.add_argument('--obj', type=str)
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--ignore_models', nargs='+')
    parser.add_argument('--allow_models', nargs='+')
    return parser.parse_args() 


def evaluate_meta_feedback_obj(
    root_dir, 
    prediction_dir, 
    ignore_models=[], 
    allow_models=[], 
    split='test', 
    domains=[
        'translate', 
        'chat', 
        'qa', 
        'harmlessness', 
        'summary', 
        'math_cot', 
        'math_pot', 
        'code_exec', 
        'code_not_exec'
    ]
):
    tables_obj = []
    tables_obj_diff = {'low': [], 'med': [], 'high': []}
    for model in os.listdir(prediction_dir):
        if ignore_models and model in ignore_models:
            print(f'[!] ignore model:', model)
            continue
        if allow_models and model not in allow_models:
            print(f'[!] ignore model:', model)
            continue
        tables_obj.append([model])
        for q in tables_obj_diff:
            tables_obj_diff[q].append([model])

        prediction_path, raw_data_path = [], []
        for domain in domains:
            raw_data_path.append(f'{root_dir}/obj_{split}_data/meta_feedback_single/meta_feedback_singlewise_{domain}.json')
            prediction_path.append(f'{prediction_dir}/{model}/{split}_{domain}_meta_feedback_obj.json')

        evalutor = EvaluateScalarMetaFeedback(
            prediction_path=prediction_path,
            raw_data_path=raw_data_path,
            split=split,
            flag='obj'
        )
        if len(evalutor.samples) == 0:
            continue
        score, diff_resp_score = evalutor.evaluate()
        tables_obj[-1].append(score)
        for q, v in diff_resp_score.items():
            tables_obj_diff[q][-1].append(v)
    table_obj = tabulate(tables_obj, headers=['models', 'Avg.'], tablefmt='simple')
    print('=' * 20, 'Meta-Feedback Objective', '=' * 20)
    print(table_obj)
    for q in tables_obj_diff:
        print('=' * 20, 'Meta-Feedback Objective Qualities', q, '=' * 20)
        table = tabulate(tables_obj_diff[q], headers=['models', 'Avg.'], tablefmt='simple')
        print(table)


if __name__ == "__main__":
    args = vars(parser_args())
    evaluate_obj(
        args['root_dir'],
        args['prediction_dir'],
        ignore_models=args['ignore_models'],
        allow_models=args['allow_models'],
        split=args['split']
    )
