from eval import evaluate_model
import argparse
import os
from ore import generate as ore_generate
from stock_model import generate as stock_generate

## Adjust these prompt modifiers as necessary for your model/system.
HUMANEVAL_PROMPT_MODIFIER = "Read the following function signature and docstring, and fully implement the function described in a ```python markdown block.\n"
MULTIPLE_CHOICE_PROMPT_MODIFIER = "\n\nThink through the problem, then provide your final answer in the form `Answer: $option_letter`.\n"
MATH_PROMPT_MODIFIER = "\nSolve this step by step, then provide your final answer in \\boxed{} format.\n"

def generate_answer(prompt, generator, config):
    output = generator(prompt, config)
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate model performance')
    # Evaluation arguments
    parser.add_argument('--use-stock', action='store_true', help='Use stock model instead of OpenReasoningEngine')
    parser.add_argument('--benchmarks', nargs='+', default=['aime'], help='List of benchmarks to run')
    parser.add_argument('--subset-name', default='micro', help='Subset name for evaluation')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of worker processes')
    
    # Model configuration arguments
    parser.add_argument('--model', default='openai/gpt-4o', help='Model identifier')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature for sampling')
    parser.add_argument('--top-p', type=float, default=1.0, help='Top-p sampling parameter')
    parser.add_argument('--max-tokens', type=int, default=4096, help='Maximum number of tokens to generate')
    parser.add_argument('--max-reasoning-steps', type=int, default=70, help='Maximum number of reasoning steps (ORE only)')
    parser.add_argument('--jeremy-planning', action='store_true', help='Enable Jeremy planning (ORE only)')
    parser.add_argument('--planning', action='store_true', help='Enable planning (ORE only)')
    parser.add_argument('--reflection', action='store_true', help='Enable reflection mode (ORE only)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create model configuration from arguments
    model_config = {
        'model': args.model,
        'temperature': args.temperature,
        'top_p': args.top_p,
        'max_tokens': args.max_tokens,
        'max_reasoning_steps': args.max_reasoning_steps,
        'use_jeremy_planning': args.jeremy_planning,
        'use_planning': args.planning,
        'reflection_mode': args.reflection,
        'verbose': args.verbose
    }
    
    generator = stock_generate if args.use_stock else ore_generate
    
    print("\nRunning with the following configuration:")
    print(f"Model: {'Stock Model' if args.use_stock else 'OpenReasoningEngine'}")
    print(f"Benchmarks: {', '.join(args.benchmarks)}")
    print(f"Subset Name: {args.subset_name}")
    print(f"Max Workers: {args.max_workers}")
    print("\nModel Configuration:")
    for key, value in model_config.items():
        print(f"{key}: {value}")
    print()
    
    evaluate_model(
        lambda prompt: generate_answer(prompt, generator, model_config),
        subset_name=args.subset_name,
        max_workers=args.max_workers,
        benchmarks=args.benchmarks,
        humaneval_prompt_modifier=HUMANEVAL_PROMPT_MODIFIER,
        multiple_choice_prompt_modifier=MULTIPLE_CHOICE_PROMPT_MODIFIER,
        math_prompt_modifier=MATH_PROMPT_MODIFIER,
    )
