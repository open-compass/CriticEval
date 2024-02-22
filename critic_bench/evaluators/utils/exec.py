import json
from latex2sympy2 import latex2sympy, latex2latex
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



# ----------- exec the code with the given input ---------- #
# refer to code base from: https://github.com/Zyq-scut/RLTF/blob/main/utils/testing_util.py#L53
# TODO: collect the error "No solution" and "alarm went off"

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    print("alarm went off")
    raise TimeoutException
signal.signal(signal.SIGALRM, timeout_handler)
timeout = 2  # seconds

def exec_math_code(code, function_name='solution', uts=[], debug=False):
    '''according to the execution results, generate PASSED, NOT PASSED'''

    if not code:
        # empty code, generate code format wrong
        return {
            'status': 'NOT PASSED',
            'detail': 'generate wrong markdown code format.',
            'answer': 'Generate wrong markdown code format.'
        }

    # add the necessary in-built packages
    sol = "import sys\nimport datetime\nimport time\nimport itertools\nfrom itertools import accumulate, product, permutations, combinations\nimport collections\nfrom collections import Counter, OrderedDict, deque, defaultdict, ChainMap\nfrom functools import lru_cache\nimport math\nfrom math import sqrt, sin, cos, tan, ceil, fabs, floor, gcd, exp, log, log2\nimport fractions\nfrom typing import List, Tuple\nimport numpy as np\nimport random\nimport heapq\nfrom heapq import *\nfrom sympy import *\n"
    sol += code
    # init the solution instance
    signal.alarm(timeout)
    try:
        tmp_sol = RuntimeModule.from_string("tmp_sol", "", sol)
        tmp = tmp_sol.Solution()
        signal.alarm(0)
    except Exception as e:
        signal.alarm(0)
        if debug:
            print(f"type 0 compilation error = {e}")
        if isinstance(e, SyntaxError):
            return {'status': 'NOT PASSED', 'answer': str(e), 'detail': str(e)}
    signal.alarm(0)
    # run the unit test

    for index, ut in enumerate(uts):
        sol_str = copy.deepcopy(sol)
        input, output = ut['input'], ut['output']
        if type(input) == str:
            input = f'"{input}"'

        returncode = None

        sol_str += f'\ninputs = {input}'.replace('inf', 'math.inf')
        sol_str += f'\nsol = Solution()'
        ## ONLY FOR MATH
        sol_str += f'\nprint(sol.solution())'

        try:
            signal.alarm(4)
            with tfile.NamedTemporaryFile(mode="w+", suffix='.py', delete=True, encoding='utf-8') as tf:
                tf.write(sol_str)
                tf.flush()
                file_path = tf.name

                render_cmd = 'python ' + file_path
                p = subprocess.Popen(render_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                returncode = p.returncode
                p.wait()
            signal.alarm(0)
            if returncode == 1:
                # error
                ans = {
                    'status': 'NOT PASSED',
                    'detail': err.decode(),
                    'answer': err.decode(),
                }
                ans['answer'] = ans['detail']
                return ans
            elif returncode == 0:
                # exection correctly
                outs = out.decode()
                outs = outs.split('\n')
                res = False
                for out in outs:
                    try:
                        res = out == str(output)
                    except:
                        pass
                    try:
                        if type(output) == float:
                            res = eval(out) == output
                        elif type(output) == int:
                            res = int(eval(out)) == output
                    except:
                        pass
                    try:
                        res = res or (float(latex2sympy(output)) == eval(out))
                    except:
                        pass
                    try:
                        res = res or (latex2sympy(output) == eval(out))
                    except:
                        pass

                    if res is True:
                        break

                if res is False:
                    return {
                        'status': 'NOT PASSED',
                        'detail': f'Unit test: {uts[index]} not passed.\nExection result: {out}\nExpected result: {output}',
                        'answer': f'Executed Result: {out}'
                    }
            else:
                raise RuntimeError('error returncode')
        except Exception as e:
            signal.alarm(0)
            p.kill()
            return {
                'status': 'NOT PASSED',
                'detail': str(e),
                'answer': str(e)
            }
        signal.alarm(0)
    return {
        'status': 'PASSED',
        'detail': 'All unit tests are correct, congratualations.',
        'answer': f'Executed Results: {out}'
    }


def exec_code(code, function_name='solution', uts=[], debug=False):
    '''according to the execution results, generate PASSED, NOT PASSED'''

    if not code:
        # empty code, generate code format wrong
        return {
            'status': 'NOT PASSED',
            'detail': 'generate wrong markdown code format.'
        }

    # add the necessary in-built packages
    sol = "import sys\nimport time\nimport itertools\nfrom itertools import accumulate, product, permutations, combinations\nimport collections\nfrom collections import Counter, OrderedDict, deque, defaultdict, ChainMap\nfrom functools import lru_cache\nimport math\nfrom math import sqrt, sin, cos, tan, ceil, fabs, floor, gcd, exp, log, log2\nimport fractions\nfrom typing import List, Tuple\nimport numpy as np\nimport random\nimport heapq\nfrom heapq import *\nfrom sympy import *\n"
    sol += code
    # init the solution instance
    signal.alarm(timeout)
    try:
        tmp_sol = RuntimeModule.from_string("tmp_sol", "", sol)
        tmp = tmp_sol.Solution()
        signal.alarm(0)
    except Exception as e:
        signal.alarm(0)
        if debug:
            print(f"type 0 compilation error = {e}")
        if isinstance(e, SyntaxError):
            return {'status': 'NOT PASSED'}
    signal.alarm(0)
    # run the unit test

    for index, ut in enumerate(uts):
        sol_str = copy.deepcopy(sol)
        input, output = ut['input'], ut['output']
        returncode = None

        if type(input) == str:
            if '\n' in input:
                input = input.replace('\n', '\\n')
        else:
            input = eval(input)

        # add the inputs and outpus into the exection file
        sol_str += f'\ninputs = "{input}"'
        sol_str += f'\nsol = Solution()'

        ## ONLY FOR Code
        sol_str += f'\nprint(sol.solution(inputs))'

        try:
            signal.alarm(2)
            with tfile.NamedTemporaryFile(mode="w+", suffix='.py', delete=True, encoding='utf-8') as tf:
                tf.write(sol_str)
                tf.flush()
                file_path = tf.name

                render_cmd = 'python ' + file_path
                p = subprocess.Popen(render_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                returncode = p.returncode
                p.wait()
            signal.alarm(0)
            p.kill()
            if returncode == 1:
                # error
                return {
                    'status': 'NOT PASSED',
                    'detail': err.decode()
                }
            elif returncode == 0:
                # exection correctly
                out = out.decode()
                out = out.split('\n')
                if out[-1] == '':
                    out = out[:-1]
                out = '\n'.join(out).lstrip().rstrip()
                res = out == str(output)

                if res is False:
                    return {
                        'status': 'NOT PASSED',
                        'detail': f'Unit test: {uts[index]} not passed.\nExection result: {out}\nExpected result: {output}'
                    }
            else:
                raise RuntimeError('error returncode')
        except Exception as e:
            signal.alarm(0)
            p.kill()
            return {
                'status': 'NOT PASSED',
                'detail': str(e)
            }
        signal.alarm(0)
    return {
        'status': 'PASSED',
        'detail': 'All unit tests are correct, congratualations.'
    }


# refer for more details: https://github.com/openai/human-eval/blob/master/human_eval/execution.py
def exec_humaneval_code(code, function_name='solution', uts=[], debug=False):
    '''according to the execution results, generate PASSED, NOT PASSED'''

    if not code:
        # empty code, generate code format wrong
        return {
            'status': 'NOT PASSED',
            'detail': 'generate wrong markdown code format.'
        }

    # add the necessary in-built packages
    sol = "import sys\nimport time\nimport itertools\nfrom itertools import accumulate, product, permutations, combinations\nimport collections\nfrom collections import Counter, OrderedDict, deque, defaultdict, ChainMap\nfrom functools import lru_cache\nimport math\nfrom math import sqrt, sin, cos, tan, ceil, fabs, floor, gcd, exp, log, log2\nimport fractions\nfrom typing import List, Tuple\nimport numpy as np\nimport random\nimport heapq\nfrom heapq import *\nfrom sympy import *\n"
    sol += code
    # init the solution instance
    signal.alarm(timeout)
    try:
        tmp_sol = RuntimeModule.from_string("tmp_sol", "", sol)
        tmp = tmp_sol.Solution()
        signal.alarm(0)
    except Exception as e:
        signal.alarm(0)
        if debug:
            print(f"type 0 compilation error = {e}")
        if isinstance(e, SyntaxError):
            return {'status': 'NOT PASSED'}
    signal.alarm(0)
    # run the unit test

    for index, ut in enumerate(uts):
        sol_str = copy.deepcopy(sol)
        input, output = ut['input'], ut['output']
        returncode = None

        if type(input) == str:
            if '\n' in input:
                input = input.replace('\n', '\\n')
        else:
            input = eval(input)

        # add the inputs and outpus into the exection file
        sol_str += f'\ninputs = "{input}"'
        sol_str += f'\nsol = Solution()'

        ## ONLY FOR Code
        sol_str += f'\nprint(sol.solution(inputs))'

        try:
            signal.alarm(2)
            with tfile.NamedTemporaryFile(mode="w+", suffix='.py', delete=True, encoding='utf-8') as tf:
                tf.write(sol_str)
                tf.flush()
                file_path = tf.name

                render_cmd = 'python ' + file_path
                p = subprocess.Popen(render_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()
                returncode = p.returncode
                p.wait()
            if returncode == 1:
                # error
                return {
                    'status': 'NOT PASSED',
                    'detail': err.decode()
                }
            elif returncode == 0:
                # exection correctly
                out = out.decode()
                out = out.split('\n')
                if out[-1] == '':
                    out = out[:-1]
                out = '\n'.join(out).lstrip().rstrip()
                res = out == str(output)

                if res is False:
                    return {
                        'status': 'NOT PASSED',
                        'detail': f'Unit test: {uts[index]} not passed.\nExection result: {out}\nExpected result: {output}'
                    }
            else:
                raise RuntimeError('error returncode')
            signal.alarm(0)
        except Exception as e:
            signal.alarm(0)
            p.kill()
            return {
                'status': 'NOT PASSED',
                'detail': str(e)
            }
        signal.alarm(0)
    return {
        'status': 'PASSED',
        'detail': 'All unit tests are correct, congratualations.'
    }


def exec_code_no_unit_test(code):
    '''only for humaneval and mbpp'''

    # add the necessary in-built packages
    sol = "import sys\nimport time\nimport itertools\nfrom itertools import accumulate, product, permutations, combinations\nimport collections\nfrom collections import Counter, OrderedDict, deque, defaultdict, ChainMap\nfrom functools import lru_cache\nimport math\nfrom math import sqrt, sin, cos, tan, ceil, fabs, floor, gcd, exp, log, log2\nimport fractions\nfrom typing import List, Tuple\nimport numpy as np\nimport random\nimport heapq\nfrom heapq import *\nfrom sympy import *\n"
    sol += code
    # run the unit test
    sol_str = copy.deepcopy(sol)
    returncode = None

    try:
        signal.alarm(2)
        with tfile.NamedTemporaryFile(mode="w+", suffix='.py', delete=True, encoding='utf-8') as tf:
            tf.write(sol_str)
            tf.flush()
            file_path = tf.name

            render_cmd = 'python ' + file_path
            p = subprocess.Popen(render_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            returncode = p.returncode
            p.wait()
        signal.alarm(0)
        p.kill()
        if returncode == 1:
            # error
            return {
                'status': 'NOT PASSED',
                'detail': err.decode()
            }
        elif returncode == 0:
            # exection correctly
            out = out.decode()
            return {
                'status': 'PASSED',
                'detail': f'{out}\nAll unit tests are correct, congratualations.'
            }
        else:
            raise RuntimeError('error returncode')
    except Exception as e:
        signal.alarm(0)
        p.kill()
        return {
            'status': 'NOT PASSED',
            'detail': str(e)
        }




if __name__ == "__main__":
    # test the exec_code function
    code = '''
    class Solution:
        def solution(self, s):
            return [''.join(s[i:i+2]) for i in range(len(s)-1)]
    '''
    uts = [{"input": "a1b2", "output": ["a1b2", "a1B2", "A1b2", "A1B2"]}, {"input": "3z4", "output": ["3z4", "3Z4"]}]
    rest = exec_code(code.strip(), uts=uts)
    ipdb.set_trace()
