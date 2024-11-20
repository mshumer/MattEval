# MattEval

An extremely simple benchmarking system for evaluating LLM performance. Define your model call as a Python function, import it in `main.py`, select a benchmark, and run the evaluation.

## Supported Benchmarks

- HumanEval
- GPQA  
- MATH
- Dharma
- AIME (2024 test subset - 10 questions that don't require vision capabilities)

## Extensibility

Adding new benchmarks is straightforward, especially for multiple choice formats. Simply upload your benchmark data and add it to `eval.py`.

That's it.
