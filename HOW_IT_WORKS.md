# TreeRefactor: Configuration and Internals

This document describes all configuration options and explains how TreeRefactor works. For a first-time setup see the [GET_STARTED.md](GET_STARTED.md).

## Configuration reference

The tool expects a TOML configuration file. Required fields:

```toml
target_file_paths = ["src/example.py"]
git_repo_path = "."
branch_name = "automatic-refactor"
refactoring_state_path = "state.json"
max_iterations = 3
show_tree = false
```

Optional fields:

```toml
root_path = "~/projects/my-project"
pyenv_name = "your-pyenv-name"
test_file_path = "."
seed = 42
temperature = 0.7
refactoring_idea_count = 3
category_attempt_count = 3
```

### Field descriptions

- `root_path` (optional, default: directory of the config file): base directory for all relative paths below
- `target_file_paths`: list of file paths to refactor, relative to `root_path`
- `git_repo_path`: path to the git repository root, relative to `root_path`
- `branch_name`: name of the branch used for the refactoring run
- `pyenv_name` (optional): Python environment name used by `pyenv` for test execution
- `test_file_path` (optional): path, relative to `root_path`, to the pytest file to run for validation. If either this or `pyenv_name` is not set, tests are skipped
- `refactoring_state_path`: path, relative to `root_path`, of the file used to persist refactoring run state
- `max_iterations`: number of refactoring iterations to attempt per file
- `show_tree`: whether to apply all evaluated refactorings or only the best one
- `seed` (default `42`): random seed used for reproducibility
- `temperature` (default: model default): sampling temperature passed to the LLM
- `refactoring_idea_count` (default `3`): number of refactoring ideas generated per attempt
- `category_attempt_count` (default `3`): number of attempts per refactoring category

## How it works

Background explanations. For setup instructions see the [GET_STARTED.md](GET_STARTED.md).

For every file in `target_file_paths`, TreeRefactor runs the following steps. Unless noted, they run once per iteration, up to `max_iterations` times per file.

1. **Setup (once per file).** The tests are run once to record a baseline (which tests pass and which fail). The readability metrics of the file are measured and committed as `chore: record initial readability metrics for <file>`.
2. **Generate.** Up to `refactoring_idea_count` of the refactoring categories that are still available are picked at random: conditional logic, control flow, method structure, expression, class structure and code quality. For each of them, the LLM is asked for exactly one small refactoring via a tool call (`extract_method`, `multi_rename`, the generic `apply_edits` that allows free edit of the code, or `no_refactoring`). A category for which the LLM answers `no_refactoring` loses one of its `category_attempt_count` attempts. When a file has no category with attempts left, its iterations end early.
3. **Evaluate.** The LLM receives each refactoring as a unified diff and returns whether behavior is preserved (`correct`), a readability grade from -3 (significantly worse) to 3 (significantly better), and a conventional-commit message.
4. **Check.** Each candidate is temporarily written to the file, then (a) compiled, (b) tested if tests are configured, and (c) measured with the readability metrics (cyclomatic complexity, Halstead, maintainability index, ...). The original code is restored after each check. Tests count as changed if any test that passed or failed in the baseline now has a different result.
5. **Select and commit.** The best valid candidate is written to the file and committed with the LLM's commit message.

### How a suggestion is selected

A candidate is **valid** only if all of these hold:

- the LLM judged it `correct` (behavior preserved),
- its readability grade is **greater than 0**,
- it compiles,
- the test results are unchanged (always true when tests are skipped).

Valid candidates are ranked by the **LLM grade**, best first. Incorrect candidates are ranked last. Ties keep the order in which the candidates were generated. The best valid candidate wins. If none is valid, nothing is committed in that iteration.

The readability metrics are stored in the commit messages, but they currently do **not** influence validity or ranking. Only the LLM grade does.

### `show_tree`

- `show_tree = false`: only the winning candidate is applied and committed on `branch_name`. The other candidates are discarded.
- `show_tree = true`: *every* evaluated candidate is committed, each on its own branch named `<file index>_<iteration>_<category>` (e.g. `0_1_EXPRESSION`; both indices start at 0). These branches branch off the commit the iteration started from, so you can compare all alternatives afterward. `branch_name` is then moved to the best valid candidate, so the main line still only follows the winner. If no candidate is valid, `branch_name` stays where it was.

### Git behavior

- The repository at `git_repo_path` must have no uncommitted or untracked changes when the run starts. If the folder is not a git repository yet, it is initialized with an initial commit.
- If `branch_name` does not exist, it is created from the current commit. If it already exists, it is checked out and reused.
- All commits go to `branch_name` (plus the per-candidate branches with `show_tree`). Your original branch is never modified. Switch back to it with `git checkout <your-branch>` afterward and merge or cherry-pick what you want to keep.

### Resuming an interrupted run

The progress (current file, iteration and remaining category attempts) is written to `refactoring_state_path` after every change. If that file exists when you start, TreeRefactor checks out `branch_name` and continues at the saved file and iteration. When all files are done, the state file is deleted. To start over, delete the state file (and the branch, if you want a clean history).

Notes:
- Add the file from the `refactoring_state_path` to .gitignore to prevent TreeRefactor from committing it every iteration.
- An interrupted run can leave a candidate written to the target file or the repository on a detached HEAD. Run `git restore .` (and `git checkout <branch_name>` if needed) before resuming, since a dirty repository is rejected.
- A resumed file records a new baseline test run and a new metrics commit.

### Data sent to the LLM provider

Everything is sent to the provider configured in the selected llm preset in [main.py](main.py). For the already configured qwen3_7_plus_config that is [OpenCode](https://opencode.ai/).

For generation TreeRefactor sends the **complete current contents of the target file** and the **messages of all commits** on the current branch (intended to keep the LLM from repeating refactorings). This includes commits from the TreeRefactor itself, as well as any pre-existing commit messages of your project. For evaluation TreeRefactor sends the **unified diff of the change** to the provider.

Don't run TreeRefactor on code or commit messages that must not leave your machine, or use a local model instead (e.g. Ollama, see the example in [llm/llm_presets.py](llm/llm_presets.py)).
