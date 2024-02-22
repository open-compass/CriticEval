from utils import *
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import transformers
from vllm import LLM, SamplingParams
import torch
from transformers.generation import GenerationConfig
from fastchat.model import load_model, get_conversation_template, add_model_args
from transformers import pipeline, LlamaTokenizer, LlamaForCausalLM
import json
import os
import sys
import ipdb
import argparse


def parser_args():
    parser = argparse.ArgumentParser(description='train parameters')
    parser.add_argument('--output_dir', type=str, default='outputs')
    parser.add_argument('--data_dir', type=str, default='../data/criticbench_v1.3')
    parser.add_argument('--split', type=str, default='test')
    parser.add_argument('--mode_name', type=str, default='feedback')
    parser.add_argument('--set_name', type=str, default='translate')
    parser.add_argument('--model_name', type=str, default='internlm/internlm2-chat-7b')
    return parser.parse_args() 


if __name__ == "__main__":
    args = vars(parser_args())
    # init the dataset
    datasets = load_all_datasets(args['data_dir'])
    
    ## init the model, revise following codes for your LLMs to be evaluated
    tokenizer = AutoTokenizer.from_pretrained(
        args['model_name'],
        trust_remote_code=True
    )
    model = AutoModelForCausalLM.from_pretrained(
        args['model_name'], 
        device_map="auto", 
        trust_remote_code=True
    ).cuda().eval()

    if os.path.exists(args['output_dir']) is False:
        os.makedirs(args['output_dir'])
    if os.path.exists(os.path.join(args['output_dir'], args['model_name'])) is False:
        os.makedirs(os.path.join(args['output_dir'], args['model_name']))
    folder_path = os.path.join(args['output_dir'], args['model_name'])

    # inference and save the results
    for abbr, dataset in tqdm(datasets.items()):
        path = os.path.join(folder_path, abbr + ".json")
        results = {}
        for item in tqdm(dataset['dev']):
            
            # If you want to inference other LLMs, please revise this line
            response, history = model.chat(tokenizer, item['question'], history=[])
            
            results[str(len(results))] = {
                'origin_prompt': item['question'],
                'prediction': response
            }
        with open(path, 'w') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
