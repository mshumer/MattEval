# humaneval/humaneval_evaluator.py

from typing import Callable, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from humaneval.eval.data import read_problems
from humaneval.eval.execution import check_correctness

import re
import random


def clean_generated_code(generated_text: str) -> str:
    """
    Extracts Python code from the generated text, removing any Markdown syntax.
    """
    # Remove markdown code blocks
    code = re.sub(r'```(?:python)?\n([\s\S]*?)```', r'\1', generated_text)
    # Remove any HTML-like tags
    code = re.sub(r'</?output>', '', code)
    # Strip leading and trailing whitespace

    # code = generated_text.split('```')[1].split('```')[0]
    code = code.strip()
    return code


def safe_check_correctness(problem: Dict, completion: str, timeout: float = 3.0) -> Dict:
    """Wrapper around check_correctness that doesn't use local functions"""
    try:
        return check_correctness(problem, completion, timeout=timeout)
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        return {
            'passed': False,
            'result': f"Error during execution: {str(e)}"
        }


def process_humaneval_example(task_id: str, prompt: str, problem: Dict,
                              generate_fn: Callable):
    """Process a single HumanEval example and return the result."""
    try:
        # Generate code
        completion = generate_fn(prompt)
        # print(completion)
        # Clean the generated code
        cleaned_code = clean_generated_code(completion)
        # print(cleaned_code)
        # Evaluate the code
        result = safe_check_correctness(problem, cleaned_code, timeout=3.0)
        result['completion'] = completion
        result['task_id'] = task_id
        return result
    except Exception as e:
        print(f"Error processing example {task_id}: {e}")
        return {
            'task_id': task_id,
            'passed': False,
            'result': f"Error: {e}",
            'completion': None,
        }


def evaluate_humaneval(
        generate_fn: Callable,
        subset_name: str = 'full',
        prompt_modifier:
    str = 'Read the following function signature and docstring, and fully implement the function described in a ```python markdown block.\n',
        n_workers: int = 4):
    """
    Evaluate the model on the HumanEval dataset.

    Args:
        generate_fn: Function that generates model responses
        subset_name: Size of the dataset to use ('micro', 'mini', or 'full')
        n_workers: Number of parallel workers to use
    """
    # Load the HumanEval problems
    problems = read_problems()

    # Determine the number of problems based on subset_name
    if subset_name == 'micro':
        num_problems = 20
    elif subset_name == 'mini':
        num_problems = 40
    elif subset_name == 'full':
        num_problems = len(problems)
    else:
        raise ValueError(f"Invalid subset name '{subset_name}'.")

    # Select a subset of problems
    problem_items = list(problems.items())
    random.seed(42)  # For reproducibility
    random.shuffle(problem_items)
    selected_problems = dict(problem_items[:num_problems])

    # Prepare a list to hold results
    results = []
    total_processed = 0
    total_passed = 0
    
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for task_id, problem in selected_problems.items():
            prompt = prompt_modifier + problem['prompt']
            future = executor.submit(process_humaneval_example, task_id,
                                     prompt, problem, generate_fn)
            futures.append(future)

        pbar = tqdm(as_completed(futures),
                   total=len(futures),
                   desc="Processing HumanEval examples")
                   
        for future in pbar:
            result = future.result()
            results.append(result)
            
            # Update counters and progress bar
            total_processed += 1
            if result.get('passed', False):
                total_passed += 1
            
            current_pass_rate = (total_passed / total_processed) if total_processed > 0 else 0
            pbar.set_description(
                f"Processing HumanEval examples | Current Pass Rate: {current_pass_rate:.2%}"
            )

    # Compute final pass@k
    pass_at_k = compute_pass_at_k(results)

    return pass_at_k['pass@1'], results


def compute_pass_at_k(results, ks=[1, 10, 100]):
    total = len(results)
    num_correct = sum(1 for result in results if result['passed'])
    pass_at_k = {}
    for k in ks:
        if total >= k:
            # For k=1, pass@1 is the fraction of correct examples
            # For other k, since we have one sample per problem, pass@k will be the same as pass@1
            pass_at_k[f'pass@{k}'] = num_correct / total
        else:
            pass_at_k[
                f'pass@{k}'] = None  # Cannot compute pass@k when total < k
    return pass_at_k
