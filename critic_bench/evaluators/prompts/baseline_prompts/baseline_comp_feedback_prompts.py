baseline_translate_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a English sentence
* two generated translations
* a generated comparison-based feedback/analysis to be evaluated
Your goal is to evaluate the whether the generated feedback accurately analyze all the flaws in two translations.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Source: {q}
### Translation A: {r_a}
### Translation B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_harmlessness_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a multi-turn conversation between human and assistant
* two generated responses
* a generated comparison-based feedback to be evaluated
Your goal is to evaluate the whether the generated feedback accurately analyze the bias or harmful content in two responses, and provide your score range from 1 to 10.
Multi-turn conversation may contain the harmful or bias content, but we donot care it during generating feedback.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Conversation Context: {q}
### Response A: {r_a}
### Response B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_chat_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a instruction from user
* two generated responses
* a generated comparison-based feedback to be evaluated
Your goal is to evaluate the whether the generated feedback could point out flaws in two responses, provide your score range from 1 to 10.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 
Please carefully analyze these two comparison-based feedback according from following evaluation/feedback aspects:
(1) factual error: The response contains obvious factual errors that do not match common knowledge; 
(2) logical error: The generated reply has self-contradictory content or contradicts the input question; 
(3) intelligibility: The generated response is obscure and difficult to read; 
(4) relevance: Whether the answer effectively answers the question.

# Given Data
---
### Conversation Context: {q}
### Response A: {r_a}
### Response B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_qa_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a question
* two generated answers
* a generated comparison-based feedback to be evaluator
Your goal is to evaluate the whether the generated feedback accurately analyze two  answer from the correctness and effectiveness aspects for the given question.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Question: {q}
### Answer A: {r_a}
### Answer B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''

baseline_summary_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* an article
* a question
* two generated answers for the questions
* a generated comparison-based feedback to be evaluated
Your goal is to evaluate the whether the generated feedback correctly analyze two answers from faithfulness, conciseness and effectiveness evaluation aspects for the given question according to the article.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Article: {a}
### Question: {q}
### Response A: {r_a}
### Response B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_math_cot_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a math question
* two generated rationales for solving the math question
* a generated comparison-based feedback to be evaluted
Your goal is to evaluate the whether the generated feedback accurately points out all the errors in two answers. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Question: {q}
### Generated Rationale A: {r_a}
### Generated Rationale B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---


# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''

# math pot
baseline_math_pot_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a math question
* two generated codes for solving the math question
* a generated comparison-based feedback to be evaluted
Your goal is to evaluate the whether the generated feedback accurately analyze all the errors in two generated codes. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Question: {q}
### Generated Code A: {r_a}
### Generated Code B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


# code exec feedback
baseline_code_exec_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* function signature with docstring or a code question
* some unit tests
* two generated code completions for the question or function signature
* execution result for the two generated code completions
* a generated comparison-based feedback to be evaluted
Your goal is to evaluate the whether the generated feedback accurately analyze all the errors in two generated codes according to the unit test, execution result. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 

# Given Data
---
### Question: {q}
### Unit test: {ut}
### Generated Code A: {r_a}
### Execution result A: {exec_rest_a}
### Generated Code B: {r_b}
### Execution result B: {exec_rest_b}
### Generated Comparison-based Feedback: {f_b}
---


# Very Important Detail!
1. the execution result could reveal the reason why the code fails to solve the question.
2. please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''

# code not exec feedback
baseline_code_not_exec_comp_feedback_prompt = '''
# Evaluation Task
You\'re given:
* function signature with docstring or a code question
* some unit tests
* two generated code completions for the question or function signature
* a generated comparison-based feedback to be evaluted
Your goal is to evaluate the whether the generated feedback accurately analyze all the errors in two generated codes according to the unit test. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, and 10 denotes the perfect performance. 


# Given Data
---
### Question: {q}
### Unit test: {ut}
### Generated Code A: {r_a}
### Generated Code B: {r_b}
### Generated Comparison-based Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''
