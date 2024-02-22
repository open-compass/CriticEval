# Inference Code for Some LLMs on CriticBench

We also provide the inference codebase for CriticBench in this folder using InternLM2 model.

This codebase could be easily converted for other LLMs by revising the `internlm2.py` file

## How to Use

Before running the codebase, please prepare the environment:

```bash
pip install -r requirements.txt
```

Then, please run the `internlm2` file for inference

```bash
CUDA_VISIBLE_DEVICES=0 python internlm2.py
```

You can easily revise this code to test your LLMs following the comments in the `internlm2.py` file.
After running this code, you could found the generation results in `outputs` folder.
