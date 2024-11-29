import re
from .exec import *

def get_exec_rest(code, unit_test, data_source):
    code = code + unit_test
    if data_source == 'humaneval':
        function_name = find_fist_function_name(code)
        code += f'\ncheck({function_name})'
    exec_rest = exec_code_no_unit_test(code)
    return exec_rest['detail']


def clean_translation(string):
    string = string.replace('来源（en）：', '')
    string = string.replace('来源：', '')
    string = string.replace('来源（英）：', '')
    string = string.replace('来源：（英）', '')
    string = string.replace('源 (en):', '')
    return string

# for humaneval dataset
def find_fist_function_name(string):
    try:
        index = string.index('def ')
        function_name = string[index:].split('\n')[0]
        f_index = function_name.index('(')
        function_name = function_name[:f_index].replace('def', '').strip()
    except:
        index = string.index('assert ')
        function_name = string[index:].split('\n')[0]
        f_index = function_name.index('(')
        function_name = function_name[:f_index].replace('assert', '').strip()
    return function_name


def extract_score(string):
    try:
        try:
            decision = re.findall('.*(Score: .+)', string)[0].replace('Score:', '').strip()
            decision = float(decision)
        except:
            try:
                decision = float(decision.split()[0])
            except:
                decision = parse_math_result(string)
    except:
        decision = None
    return decision


def extract_decision(string):
    try:
        try:
            decision = re.findall('.*(Decision: .+)', string)[0].replace('Decision:', '').strip()
            decision = float(decision)
        except:
            try:
                decision = float(decision.split()[0])
            except:
                decision = parse_math_result(string)
    except:
        decision = None
    return decision


def extract_decision_float(string):
    try:
        try:
            decision = re.findall('Score: (\d+\.\d+|\d+)', string)
            decision = float(decision[0])
        except Exception as error:
            try:
                decision = float(decision.split()[0])
            except:
                decision = parse_math_result(string)
    except:
        decision = None
    return decision


def extract_decision_option(string):
    try:
        decision = re.findall('.*(Decision: .+)', string)[0].replace('Decision:', '').strip()
    except:
        decision = string.replace('.', '').strip()
    return decision

    
def extract_likert(string):
    decision = re.findall('.*(Likert: .+)', string)[0].replace('Likert:', '').strip()
    try:
        decision = int(decision[0])
    except:
        decision = ''
    return decision


'''
def parse_math_result(string):
    try:
        decision = re.findall('.*(#### .+)', string)[0].replace('####', '').strip()
    except:
        return ''
    # decision = decision.replace('RESULT:', '').strip()
    predictions = decision.split()
    res = None
    for v in predictions:
        try:
            if eval(v):
                if type(eval(v)) == float or type(eval(v)) == int:
                    res = eval(v)
                    break
        except:
            pass
    if res:
        decision = res
    else:
        decision = ''
    return decision
'''
def parse_math_result(string):
    '''最终答案肯定在后面，我们从后面parse数字即可'''
    try:
        if type(string) == dict:
            if 'Rationale' in string:
                string = string['Rationale']
            elif 'rationale' in string:
                string = string['rationale']
            elif 'Answer' in string:
                string = ' ' + string['Answer'] + ' '
            else:
                ipdb.set_trace()
        string = string.replace('\n', ' ').replace('=', '= ')
        res = None
        for v in reversed(string.split()):
            try:
                if eval(v):
                    if type(eval(v)) == float or type(eval(v)) == int:
                        res = eval(v)
                        break
            except:
                pass
        if res:
            decision = res
        else:
            decision = ''
    except:
        return ''
    return decision


def parse_code(code, lang='python'):
    pattern = rf'```{lang}.*?\s+(.*?)```'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        code_ = match.group(1)
    else:
        # print(f'do not match any code from: {code}')
        if '```python' not in code and '```' not in code:
            return code
        else:
            return ''
    return code_
