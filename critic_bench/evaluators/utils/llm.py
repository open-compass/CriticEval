import json
import httpcore
import sys
from multiprocessing import Pool
from openai import OpenAI
import openai
import copy
import subprocess
from pyext import RuntimeModule
import signal
import tempfile as tfile
import requests
import ipdb
import pprint
import time
from tqdm import tqdm
import subprocess


def _prepare_input(payload, temp, max_tokens, llm_name):
    input_data = {
        'model': llm_name,
        'messages': payload['messages'],
        'temperature': temp
    }
    return input_data


def _chat_one_sessiona_personal(payload, sleep_time, retry_num, temp, max_tokens, llm_name, index):

    def _generate_single(
        client,
        prompt: str,
        # model: str = 'gpt-4-1106-preview',
        model: str = 'gpt-3.5-turbo',
        **kwargs
    ) -> dict:
        success = False
        completion = None
        while not success:
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                success = True
                print(f'[!] one try success')
            except httpcore.RemoteProtocolError or httpcore.ConnectTimeout:
                print(f'[!] one try failed')
                time.sleep(20)
                sys.stdout.flush()

        return {
            "generation": completion.choices[0].message.content,
            **kwargs
        }
    client = OpenAI()
    input_data = _prepare_input(payload, temp, max_tokens, llm_name)
    data = _generate_single(client, input_data['messages'][0]['content'])
    response = data['generation']
    return response, index



def batch_chat(payloads, sleep_time=20, retry_num=1000, temp=0.5, max_tokens=4096, model_name='gpt-4-1106-preview', debug=False):
    if debug is True:
        for index, payload in enumerate(payloads):
            _chat_one_sessiona_personal(payload, sleep_time, retry_num, temp, max_tokens, model_name, index)
    else:
        pool = Pool(processes=2)
        result_list = []
        for index, payload in enumerate(payloads):
            result_list.append(
                pool.apply_async(
                    _chat_one_sessiona_personal, 
                    (
                        payload, 
                        sleep_time, 
                        retry_num, 
                        temp, 
                        max_tokens, 
                        model_name, 
                        index
                    )
                )
            )
        pool.close()
        pool.join()
        values = [rest.get() for rest in result_list]
        sorted_values = sorted(values, key=lambda x:x[1])
        sorted_values = [i[0] for i in sorted_values]
        return sorted_values


if __name__ == "__main__":
    response = batch_chat([
            {
                'model': 'gpt-4-1106-preview',
                'messages': [
                    {
                        'role': 'user',
                        'content': 'who are you?'
                    }    
                ]
            },
        ],
        temp=0,
        model_name='gpt-4-1106-preview',
        debug=True
    )
    print(response)
