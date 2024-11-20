# MattEval

An extremely simple, batteries-included benchmarking system for evaluating LLM performance. Define your model call as a Python function, import it in `main.py`, select a benchmark, and run the evaluation.

## Included Benchmarks

- HumanEval
- GPQA  
- MATH (requires an OpenAI API key for correctness evaluation)
- Dharma
- AIME (2024 test subset - 10 questions that don't require vision capabilities)

## Prompt Modifiers

- Some benchmarks require outputs to follow a specific format (i.e. MATH wants a boxed answer). Given we are now in the era of systems, rather than pure models, and prompting strategies vary, you can adjust how we ask for the format by adjusting the prompt modifiers in `main.py`.

## Extensibility

Adding new benchmarks is straightforward, especially for multiple choice formats. Simply upload your benchmark data and add it to `eval.py`.

That's it.
