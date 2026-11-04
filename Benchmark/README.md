# PythonRefactoringBenchmark

A benchmark for evaluating automatic Python refactoring tools against popular open-source projects, using each project's own test suite as the correctness check.

It was built to evaluate **TreeRefactor** and **AutoRefactor**, but the setup is tool-agnostic - anything that can take a target file, a test file, and a pyenv environment can use this setup.

## Targets

| Project | Version | File to refactor | Test file |
|---|---|---|---|
| requests | 2.34.2 | [`requests/requests-2.34.2/src/requests/utils.py`](requests/requests-2.34.2/src/requests/utils.py) | `requests/requests-2.34.2/tests/test_utils.py` |
| matplotlib | 3.11.1 | `matplotlib/backends/backend_agg.py` | `matplotlib/tests/test_agg.py` |
| pandas | 3.0.5 | `pandas/core/indexes/multi.py` | `pandas/tests/indexes/multi/test_sorting.py` |
| pytorch | 2.13.0 | `torch/fx/passes/pass_manager.py` | `torch/fx/passes/tests/test_pass_manager.py` |

matplotlib and pandas share an environment since they're tested against the same Python/pyenv version; pytorch needs an older Python and gets its own. The requests source and matplotlib's image-comparison test fixtures are **not** included in this repository - `setup.sh` downloads them from their official GitHub repositories at the pinned versions. matplotlib, pandas and pytorch are refactored in place inside their pyenv site-packages.

## Environments

| pyenv env | Python | Site-packages |
|---|---|---|
| `requests` | 3.14.3 | `requests/requests-2.34.2` (downloaded by `setup.sh`) |
| `matplotlib-pandas` | 3.14.3 | `~/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages` |
| `pytorch` | 3.10.16 | `~/.pyenv/versions/3.10.16/envs/pytorch/lib/python3.10/site-packages` |

## Layout

- `setup.sh` — provisions the pyenv virtualenvs above, downloads the requests source and the matplotlib [image-comparison test fixtures](https://matplotlib.org/devdocs/devel/testing.html) at the pinned versions, installs the pinned package versions from the Targets table, copies in the test fixtures, and runs each target's test file once as a sanity check.
- `*_config.toml` — one config per target, consumed by TreeRefactor as a CLI argument. Points it at the file to refactor, the matching test file, the pyenv environment to run it in, and run parameters (seed, temperature, iteration/attempt limits, etc.).
- `requests/` — created by `setup.sh`, gitignored: the requests source tree that TreeRefactor refactors.

## Setup

Requires [pyenv](https://github.com/pyenv/pyenv) with the `pyenv-virtualenv` plugin, as well as `curl` and `tar`, on Linux.

```bash
./setup.sh
```

This creates the three virtualenvs above, downloads and installs the pinned versions, and runs each project's relevant test file to confirm the environment is healthy before any refactoring happens.

## Licensing

The requests source and the matplotlib baseline image fixtures are unmodified third-party source and test assets, downloaded at pinned versions from their official repositories and used solely to make the benchmark reproducible. Each carries its original project's license (requests: [Apache 2.0](https://github.com/psf/requests/blob/main/LICENSE); matplotlib: [its own license](https://github.com/matplotlib/matplotlib/blob/main/LICENSE/LICENSE_1.txt)). Everything else in this repo — the configs, scripts, and this README — is provided under the [MIT License](../LICENSE) of the TreeRefactor repository.
