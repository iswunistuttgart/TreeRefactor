import argparse
import random
from dataclasses import replace
from pathlib import Path

from llm.llm_presets import qwen3_7_plus_config
from llm.openai_llm import OpenAILLM
from llm.parallel_llm import ParallelLLM
from llm.retrying_llm import RetryingLLM
from refactoring_system import RefactoringSystem
from utility.cli import CLI
from utility.config import load_from_toml

if __name__ == '__main__':
    CLI.set_debug_mode(True) # Enable debug mode for detailed output

    # Set up argument parser to accept config file path
    parser = argparse.ArgumentParser(description='Automatic Python Refactoring Tool')
    parser.add_argument('config_path', help='Path to config file')
    args = parser.parse_args()

    # Load configuration from the specified TOML file
    full_config_path = Path(args.config_path).absolute().resolve()
    config = load_from_toml(full_config_path)

    # Set random seed for reproducibility
    random.seed(config.seed)
    # Set up LLM configuration with specified temperature
    llm_config = replace(qwen3_7_plus_config, temperature=config.temperature)

    print("Running the refactoring system with the following parameters:")
    print(str(config))

    llm = ParallelLLM(RetryingLLM(OpenAILLM(llm_config),
                      max_retries=3, delay_seconds=10.0))
    refactoring_system = RefactoringSystem(config, llm)
    refactoring_system.run()
