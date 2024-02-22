from .formats import mappings
from .prompts import prompts
from .critic_bench_dataloader import *


def load_all_datasets(root_dir='../../data/criticbench_v1.3', split='test', mode_name='feedback', set_name='translate'):
    # set_names = [
    #     'translate',
    #     'qa',
    #     'chat',
    #     'summary',
    #     'harmlessness',
    #     'math_cot',
    #     'math_pot',
    #     'code_exec',
    #     'code_not_exec'
    # ]
    criticbench_datasets = {}
    # meta-feedback only have objective evaluation
    flags = ['obj'] if mode_name in ['meta_feedback'] else ['sub', 'obj']
    for flag in flags:
        if flag == 'obj' and mode_name == 'correction':
            # correction objective evaluation only have math_cot, math_pot, code_exec, and code_not_exec
            if set_name not in ['math_cot', 'math_pot', 'code_exec', 'code_not_exec']:
                continue
        elif flag == 'sub' and mode_name == 'correction':
            # correction subjective evaluation must not be math_cot, math_pot, code_exec, and code_not_exec
            if set_name in ['math_cot', 'math_pot', 'code_exec', 'code_not_exec']:
                continue

        if mode_name in ['feedback', 'comp_feedback']:
            prefix_prompt = prompts[mode_name][flag][set_name]['prefix_prompt']
            post_prompt = prompts[mode_name][flag][set_name]['post_prompt']
        else:
            prefix_prompt = prompts[mode_name][set_name]['prefix_prompt']
            post_prompt = prompts[mode_name][set_name]['post_prompt']

        if mode_name in ['feedback', 'correction']:
            data_path = f'{flag}_{split}_data/{set_name}_feedback_correction.json'
        elif mode_name  == 'comp_feedback':
            data_path = f'{flag}_{split}_data/{set_name}_comp_feedback.json'
        else:
            data_path = f'{flag}_{split}_data/meta_feedback_single/meta_feedback_singlewise_{set_name}.json'

        criticbench_datasets[f'{split}_{set_name}_{mode_name}_{flag}'] = load_dataset(
            path=root_dir,
            name=data_path,
            flag_name=flag,
            domain_name=set_name,
            mode_name=mode_name,
            mappings=mappings,
            prefix_prompt=prefix_prompt,
            post_prompt=post_prompt,
        )
        # append the correct part feedback
        if mode_name == 'feedback' and set_name != 'code_exec':
            data_path = f'{set_name}_feedback.json'
            criticbench_datasets[f'{split}_{set_name}_{mode_name}_{flag}_correction_part'] = load_dataset(
                path=f'{root_dir}/{flag}_{split}_data/correction_part',
                name=data_path,
                flag_name=flag,
                domain_name=set_name,
                mode_name=mode_name,
                mappings=mappings,
                prefix_prompt=prefix_prompt,
                post_prompt=post_prompt,
            )
    # append the new objective dataset with reversed position
    if mode_name in ['comp_feedback']:
        data_path = f'obj_{split}_data/{set_name}_comp_feedback.json'
        criticbench_datasets[f'{split}_{set_name}_{mode_name}_obj_reverse'] = load_dataset(
            path=root_dir,
            reverse=True,
            name=data_path,
            flag_name='obj',
            domain_name=set_name,
            mode_name=mode_name,
            mappings=mappings,
            prefix_prompt=prefix_prompt,
            post_prompt=post_prompt,
        )
    return criticbench_datasets
