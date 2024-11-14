import re
import csv
import random
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Dict
from datasets import load_dataset
from tqdm.auto import tqdm
import pandas as pd
import requests
import json


def load_dharma_subset(subset_name):
    """Load the specified subset of the Dharma dataset."""
    subset_files = {
        'full': 'dharma_1_full.json',
        'mini': 'dharma_1_mini.json',
        'micro': 'dharma_1_micro.json'
    }
    data_file = subset_files.get(subset_name)
    if data_file is None:
        raise ValueError(
            f"Invalid subset name '{subset_name}'. Available subsets: {list(subset_files.keys())}"
        )

    dataset = load_dataset('pharaouk/dharma-1',
                           data_files={'train': data_file},
                           split='train')
    return dataset


def load_gpqa_questions(subset_name, seed=42):
    """Load GPQA questions according to the subset and return a list of examples."""
    # Set seed for reproducibility
    random.seed(seed)

    with open("gpqa.csv", "r", encoding='utf-8') as f:
        gpqa_dict = list(csv.DictReader(f))

    # Determine the number of GPQA questions to use
    if subset_name == 'micro':
        num_questions = 20
    elif subset_name == 'mini':
        num_questions = 90
    elif subset_name == 'full':
        num_questions = len(gpqa_dict)
    else:
        raise ValueError(f"Invalid subset name '{subset_name}'.")

    # Shuffle the GPQA questions
    random.shuffle(gpqa_dict)

    # Select the desired number of questions
    gpqa_dict = gpqa_dict[:num_questions]

    # Now, for each GPQA question, build the prompt and get the correct answer letter
    gpqa_examples = []
    for item in gpqa_dict:
        question = item['Question']
        possible_answers = [
            item['Incorrect Answer 1'], item['Incorrect Answer 2'],
            item['Incorrect Answer 3'], item['Correct Answer']
        ]
        correct_answer = item['Correct Answer']
        # Shuffle the possible answers
        random.shuffle(possible_answers)
        # Assign letters to options
        possible_answers_with_letters = []
        for i, answer in enumerate(possible_answers):
            possible_answers_with_letters.append(f"{chr(65 + i)}. {answer}")

        prompt = f"{question}\n\n{possible_answers_with_letters[0]}\n{possible_answers_with_letters[1]}\n{possible_answers_with_letters[2]}\n{possible_answers_with_letters[3]}\n\nAnswer:"

        # Get the correct answer letter
        correct_answer_letter = chr(65 +
                                    possible_answers.index(correct_answer))

        # Build the example
        example = {
            'input': prompt,
            'target': correct_answer_letter,
            'subject': 'GPQA'
        }
        gpqa_examples.append(example)

    return gpqa_examples


def load_aime_questions():
    """Load AIME questions from the JSON file and return a list of examples."""
    with open('aime/questions.json', 'r', encoding='utf-8') as f:
        aime_questions = json.load(f)

    aime_examples = []
    for item in aime_questions:
        example = {
            'input': item['question'],
            'target': item['answer'],
            'subject': 'AIME'
        }
        aime_examples.append(example)

    return aime_examples
    
def number_to_letter(number):
    """Convert a number (1-26) to corresponding letter (A-Z)"""
    try:
        num = int(number)
        if 1 <= num <= 26:
            return chr(64 + num)
        return number
    except ValueError:
        return number


def extract_letter_answer(generated_text):
    """Extract the bottom-most answer from the generated text.

    Supports formats:
    - "Answer: A" or "Ans: A"
    - "The answer is A"
    - Single letter/number answers

    Args:
        generated_text (str): Text containing the answer

    Returns:
        str: Extracted answer converted to letter format
    """
    # Pattern for "Answer: A" or "Ans: A"
    pattern1 = r'(?:Answer|Ans)\s*[:\-]?\s*([A-Z0-9])\b'

    # Pattern for "The answer is A"
    pattern2 = r'answer is\s+([A-Z0-9])\b'

    # Try first pattern (Answer: A)
    matches = re.findall(pattern1, generated_text, re.IGNORECASE)
    if matches:
        return number_to_letter(matches[-1])

    # Try second pattern (The answer is A)
    matches = re.findall(pattern2, generated_text, re.IGNORECASE)
    if matches:
        return number_to_letter(matches[-1])

    # Fall back to finding single letters/numbers
    matches = re.findall(r'\b([A-Z0-9])\b', generated_text)
    if matches:
        return number_to_letter(matches[-1])

    # If no matches found, return stripped text
    return generated_text.strip()

def extract_numeric_answer(generated_text):
    """Extract the bottom-most numeric answer from the generated text.

    Supports extraction of numeric answers, including integers and decimals.

    Args:
        generated_text (str): Text containing the answer

    Returns:
        str: Extracted numeric answer as a string
    """
    # Remove commas in numbers
    generated_text = generated_text.replace(',', '')

    # Pattern to match numbers (integers and decimals)
    pattern = r'[-+]?\b\d+(?:\.\d+)?\b'

    # Find all numbers in the generated text
    matches = re.findall(pattern, generated_text)

    if matches:
        # Return the last number found
        numbers = re.findall(pattern, generated_text)
        return numbers[-1]
    else:
        # If no numbers found, return the entire text stripped
        return generated_text.strip()

def extract_answer(generated_text, subject):
    """Route to the appropriate extract_answer function based on subject."""
    if subject in ['GPQA', 'dharma']:
        return extract_letter_answer(generated_text)
    elif subject == 'AIME':
        return extract_numeric_answer(generated_text)
    else:
        # Default to letter answer extraction
        return extract_letter_answer(generated_text)

def process_example(example: Dict, generate_fn: Callable) -> Dict:
    """Process a single example and return the results."""
    input_text = example['input']
    target = example['target']
    subject = example['subject']

    try:
        generated_answer = generate_fn(input_text)
        extracted_answer = extract_answer(generated_answer, subject)
        correct = (extracted_answer.strip() == target.strip())

        return {
            'subject': subject,
            'correct': correct,
            'input': input_text,
            'target': target,
            'generated_answer': generated_answer,
            'extracted_answer': extracted_answer,
            'error': None
        }
    except Exception as e:
        return {
            'subject': subject,
            'correct': False,
            'input': input_text,
            'target': target,
            'generated_answer': None,
            'extracted_answer': None,
            'error': str(e)
        }


class ScoreTracker:

    def __init__(self):
        self.total = 0
        self.correct = 0

    def update(self, result):
        if not result['error']:
            self.total += 1
            if result['correct']:
                self.correct += 1

    @property
    def accuracy(self):
        if self.total == 0:
            return 0
        return self.correct / self.total


def evaluate_model(
    generate_fn: Callable,
    subset_name: str = 'full',
    max_workers: int = 4,
    benchmarks: List[str] = ['gpqa', 'dharma', 'humaneval', 'aime'],
    multiple_choice_prompt_modifier='Answer:',
    humaneval_prompt_modifier="Read the following function signature and docstring, and fully implement the function described in a ```python markdown block.\n"
):
    """
    Evaluate the model on specified benchmarks using parallel processing with live scoring updates.
    
    Args:
    generate_fn: Function that generates model responses
    subset_name: Size of the dataset to use ('micro', 'mini', or 'full')
    max_workers: Number of parallel workers to use
    benchmarks: List of benchmarks to evaluate ('gpqa', 'dharma', 'humaneval')
    """
    examples = []
    print('Evaluating.')

    # Load GPQA examples if specified
    if 'gpqa' in benchmarks:
        print("Loading GPQA examples...")
        gpqa_examples = load_gpqa_questions(subset_name, seed=42)
        examples.extend(gpqa_examples)

    # Load Dharma dataset if specified
    if 'dharma' in benchmarks:
        print("Loading Dharma examples...")
        dataset = load_dharma_subset(subset_name)
        dharma_examples = [{
            'input': input_text,
            'target': target,
            'subject': subject
        } for input_text, target, subject in zip(
            dataset['input'], dataset['output'], dataset['subject'])]
        examples.extend(dharma_examples)

    # Load AIME examples if specified
    if 'aime' in benchmarks:
        print("Loading AIME examples...")
        aime_examples = load_aime_questions()
        examples.extend(aime_examples)

    # Process GPQA and Dharma examples if any
    # Process GPQA and Dharma examples if any
    results = []
    if examples:
        for example in examples:
            example['input'] = example['input'].replace(
                'Answer:', multiple_choice_prompt_modifier)

        print("Processing GPQA, AIME, and/or Dharma examples...")
        score_tracker = ScoreTracker()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_example = {
                executor.submit(process_example, example, generate_fn): example
                for example in examples
            }

            pbar = tqdm(as_completed(future_to_example),
                        total=len(examples),
                        desc="Processing examples")
            for future in pbar:
                result = future.result()
                results.append(result)

                # Update score tracker and progress bar description
                score_tracker.update(result)
                pbar.set_description(
                    f"Processing examples | Current Accuracy: {score_tracker.accuracy:.2%}"
                )

                if result['error']:
                    print(f"Error processing example: {result['error']}")

        # Compute per-subject scores
        subject_results = defaultdict(list)
        for res in results:
            if not res['error']:
                subject_results[res['subject']].append(res['correct'])

        subject_scores = {
            subject: sum(results_list) / len(results_list)
            for subject, results_list in subject_results.items()
        }

        # Display results
        df = pd.DataFrame({
            'Subject':
            list(subject_scores.keys()),
            'Accuracy':
            [f"{accuracy:.2%}" for accuracy in subject_scores.values()]
        })
        df = df.sort_values(by='Accuracy', ascending=False)
        print("\nPer-Subject Accuracy:")
        print(df.to_string(index=False))

        print(f"\nFinal Overall Accuracy: {score_tracker.accuracy:.2%}")

    # Evaluate HumanEval if specified
    if 'humaneval' in benchmarks:
        from humaneval.eval.humaneval_evaluator import evaluate_humaneval
        print("Evaluating on HumanEval dataset...")
        humaneval_results, outputs_results = evaluate_humaneval(
            generate_fn,
            subset_name=subset_name,
            prompt_modifier=humaneval_prompt_modifier,
            n_workers=max_workers)
        print(f"Final HumanEval Accuracy: {humaneval_results}")
        # print(outputs_results)

    # Return combined results if needed
    return {
        'gpqa_dharma_results':
        results if examples else None,
        'humaneval_results':
        humaneval_results if 'humaneval' in benchmarks else None
    }
