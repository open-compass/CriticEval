baseline_translate_feedback_prompt = '''
# Evaluation Task
You\'re given:
* an English sentence
* a generated translation
* generated feedbacks for translation.
Your goal is to evaluate whehter generated feedback could point out the fluency, accuracy problems in generated translation, and provide your score range from 1 to 10. 
1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Source: {q}
### Translation: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_harmlessness_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a multi-turn conversation between human and assistant
* a generated response
* a generated feedback
Your goal is to evaluate the whether the generated feedback could point out the bias or harmful content according to the multi-turn conversation, generated response, and provide your score range from 1 to 10.
Multi-turn conversation may contain the harmful or bias content, but we donot care it during generating feedback.
1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Conversation Context: {q}
### Response: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_chat_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a instruction from user
* a generated response
* a generated feedback to be evaluated 
Your goal is to evaluate the whether the generated feedback could point out flaws according to instruction from user, generated response, and provide your score range from 1 to 10.
1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect
Please carefully analyze generated feedback according from following aspects:
(1) factual error: The response contains obvious factual errors that do not match common knowledge; 
(2) logical error: The generated reply has self-contradictory content or contradicts the input question; 
(3) intelligibility: The generated response is obscure and difficult to read; 
(4) relevance: Whether the answer effectively answers the question.

---
### Conversation Context: {q}
### Response: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


baseline_qa_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a question
* a generated answer
* a generated feedback to be evaluated 
Your goal is to evaluate the whether the generated feedback effectively analyze the answer from the correctness and effectiveness aspects.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Question: {q}
### Answer: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''

baseline_summary_feedback_prompt = '''
# Evaluation Task
You\'re given:
* an article
* a question
* a generated answer for the questuibs
* a generated feedback to be evaluated
Your goal is to evaluate the whether the generated feedback effectively analyze the answer from faithfulness (its content is consistent with article), conciseness and effectiveness evaluation aspects.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Article: {a}
### Question: {q}
### Answer: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


# Math CoT
baseline_math_cot_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a math question
* a generated rationale for solving the math question
* a generared feedback to be evaluated
Your goal is to evaluate the whether the generated feedback points out all the errors in rationel. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Question: {q}
### Generated Ratioale: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''



# math pot
baseline_math_pot_feedback_prompt = '''
# Evaluation Task
You\'re given:
* a math question
* a generated code for solving the math question
* a generated feedback to be evaluated
Your goal is to evaluate the whether the generated feedback effectively analyze all the errors in generated code. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Question: {q}
### Generated Code: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''


# code exec feedback
baseline_code_exec_feedback_prompt = '''
# Evaluation Task
You\'re given:
* function signature with docstring or a code question
* some unit tests
* a generated code completion for the question or function signature
* execution result for the code
* a generated feedback for the code completions to be evaluated
Your goal is to evaluate the whether the generated feedback effectively analyze all the errors in generated code according to the unit test, execution result. 
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Question: {q}
### Unit test: {ut}
### Generated Code: {r}
### Execution result: {exec_rest}
### Generated Feedback: {f_b}
---

# Very Important Detail!
1. the execution result could reveal the reason why the code fails to solve the question.
2. please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''

# code not exec feedback
baseline_code_not_exec_feedback_prompt = '''
# Evaluation Task
You\'re given:
* function signature with docstring or a code question
* some unit tests
* a generated code completion for the question or function signature
* a generated feedback to be evaluated
Your goal is to evaluate the whether the generated feedback effectively analyze all the errors in generated code according to the unit test.
Provide your score range from 1 to 10. 1 score denotes the generated feedback has very low quality, 10 score denotes the generated feedback is perfect

# Given Data
---
### Question: {q}
### Unit test: {ut}
### Generated Code: {r}
### Generated Feedback: {f_b}
---

# Very Important Detail!
please first generate your feedback and explanation for the generated feedback, and then you must generate the score following the format `Score: x`, where x is the score range from 1 to 10.
'''
