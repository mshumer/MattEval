from eval import evaluate_model
from ore import generate

def generate_answer(prompt):
    output = generate(prompt, 0.5, 1)
    return output

if __name__ == '__main__':
    evaluate_model(
        generate_answer,
        subset_name='micro',
        max_workers=8,
        benchmarks=['humaneval'],
        humaneval_prompt_modifier=
        '''Read the following function signature and docstring, and fully implement the function described in a ```python markdown block.\n''',
        multiple_choice_prompt_modifier='\n\nThink through the problem, then provide your final answer in the form `Answer: $option_letter`.\n'
    )
