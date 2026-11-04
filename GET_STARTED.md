# Getting started with TreeRefactor

A step-by-step guide for the first run. How the tool works internally and all configuration options are explained in [HOW_IT_WORKS.md](HOW_IT_WORKS.md).

## 1. Install Dependencies

Ensure Python 3.14 and Git are installed.
Install the Python libraries in an environment from the TreeRefactor folder:
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

[`pyenv`](https://github.com/pyenv/pyenv) is only needed if you want the target project's tests to be run (see step 4). It can also be used to create the environment.

## 2. Configure the LLM

Configurations for LLM endpoints can be created in [llm/llm_presets.py](llm/llm_presets.py) and selected in [main.py](main.py). 

We provide the `qwen3_7_plus_config` which can be used with an OpenCode Go subscription. Create a `.env` file in the TreeRefactor root containing its API key:
```
OPENCODE_GO_API_KEY=your-api-key
```

To use another provider or a local model, create your own preset in [llm/llm_presets.py](llm/llm_presets.py) by following the descriptions and select it in [main.py](main.py) (replace the `qwen3_7_plus_config` import and the `replace(qwen3_7_plus_config, ...)` call). 

Note: `qwen3_7_plus_config` reads `OPENCODE_GO_API_KEY` as soon as `llm/llm_presets.py` is imported, so TreeRefactor fails at startup with a `ValueError` if that variable is missing. When you don't use OpenCode Go, delete or comment out `qwen3_7_plus_config` in [llm/llm_presets.py](llm/llm_presets.py) and no `.env` file is needed.

## Running the benchmark
For running the benchmark from the paper steps 3 to 5 can be skipped. The benchmark is contained in the [Benchmark](Benchmark/) folder; set it up as described in [Benchmark/README.md](Benchmark/README.md). It contains the config files pandas_config.toml, pytorch_config.toml, matplotlib_config.toml and requests_config.toml. These are passed to TreeRefactor, when proceeding with step 6.

Note: It is suggested to add refactoring_state.json to the global .gitignore or to all repositories separately to prevent Git from tracking TreeRefactor's state unnecessarily.

## 3. Prepare the project to refactor

- It has to be a git repository without uncommitted or untracked changes. (If the folder is no repository yet, one is created.)
- Add the state file (`refactoring_state_path`, e.g. `state.json`) to that project's `.gitignore`. Otherwise it is committed in every iteration.

## 4. (Optional) Set up the pyenv environment

The project's tests are run with `pyenv exec pytest` in the pyenv environment named by `pyenv_name`. That environment needs the *target project's* dependencies and `pytest`. It is independent of the environment TreeRefactor runs in. Example with `pyenv-virtualenv`:

```bash
pyenv install 3.12            # any version your target project supports
pyenv virtualenv 3.12 my-project-env
PYENV_VERSION=my-project-env pyenv exec pip install pytest -r /path/to/my-project/requirements.txt
```

If you skip this step, leave `pyenv_name` and `test_file_path` out of the config. Refactorings are then only checked by compilation and the LLM evaluation.

## 5. Write the configuration file

Save this as e.g. `~/refactoring/config.toml` and adapt it. All paths are relative to the directory of the config file, or to `root_path` if you set it. All fields are described in the [configuration reference](HOW_IT_WORKS.md#configuration-reference).

```toml
root_path = "~/projects/my-project"         # optional, default: directory of this file

target_file_paths = ["src/my_module.py", "src/other_module.py"]
git_repo_path = "."
branch_name = "automatic-refactor"
refactoring_state_path = "state.json"
max_iterations = 3
show_tree = false

# Remove these two lines to skip running tests
pyenv_name = "my-project-env"
test_file_path = "tests"
```

## 6. Run it

```bash
python main.py ~/refactoring/config.toml
```

## 7. Review the result

The refactorings are committed on `branch_name` (and, with `show_tree`, on one extra branch per candidate). Your original branch is untouched. Inspect the result, then merge or cherry-pick what you want.

If the run is interrupted, start it again with the same command. See [Resuming an interrupted run](HOW_IT_WORKS.md#resuming-an-interrupted-run).
