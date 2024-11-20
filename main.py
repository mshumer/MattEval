from eval import evaluate_model
from ore import generate

## Adjust these prompt modifiers as necessary for your model/system.
HUMANEVAL_PROMPT_MODIFIER = "Read the following function signature and docstring, and fully implement the function described in a ```python markdown block.\n"
MULTIPLE_CHOICE_PROMPT_MODIFIER = "\n\nThink through the problem, then provide your final answer in the form `Answer: $option_letter`.\n"
MATH_PROMPT_MODIFIER = "\nSolve this step by step, then provide your final answer in \\boxed{} format.\n"

def generate_answer(prompt):
    output = generate(prompt, 0.5, 1)
    return output

if __name__ == '__main__':
    evaluate_model(
        generate_answer,
        subset_name='micro',
        max_workers=8,
        benchmarks=['humaneval'],
        humaneval_prompt_modifier=HUMANEVAL_PROMPT_MODIFIER,
        multiple_choice_prompt_modifier=MULTIPLE_CHOICE_PROMPT_MODIFIER,
        math_prompt_modifier=MATH_PROMPT_MODIFIER,
    )
