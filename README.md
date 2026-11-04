# TreeRefactor 

TreeRefactor is a Python project for automated code refactoring with Large Language Models (LLMs).

## Documentation

- [GET_STARTED.md](GET_STARTED.md) – step-by-step guide for the first run
- [EXTENDING.md](EXTENDING.md) – how to add a new refactoring tool, with an example and tests
- [HOW_IT_WORKS.md](HOW_IT_WORKS.md) – configuration reference and explanation of the workflow, selection criteria, git behavior and data sent to the LLM provider

## Project structure

- [main.py](main.py) – CLI entry point for running the tool
- [refactoring_system.py](refactoring_system.py) – orchestrates the refactoring workflow
- [refactoring/](refactoring/) – implementation of refactorings types and tools 
- [llm/](llm/) – LLM integrations and prompt handling
- [tree_of_thoughts/](tree_of_thoughts/) – generation and evaluation logic
- [utility/](utility/) – configuration, git handling, testing, and analysis helpers
- [Benchmark/](Benchmark/) – the benchmark used in the paper: configs and setup script for the four target projects

## Requirements

- TreeRefactor was developed for **Python 3.14**
- Git must be installed as TreeRefactor uses it
- **[pyenv](https://github.com/pyenv/pyenv)**: only needed if the target project's tests should be run (see [GET_STARTED.md](GET_STARTED.md#4-optional-set-up-the-pyenv-environment)).
- Local or hosted LLM with OpenAI-compatible endpoint
- the needed Python libraries can be installed from the [requirements.txt](requirements.txt)

## License

Distributed under the [MIT License](LICENSE).
