#!/bin/bash

# Provisions the pyenv environments for the four benchmark targets and runs each
# target's test file once as a sanity check.
# Requires: pyenv with the pyenv-virtualenv plugin, curl, tar. Run on Linux from this folder.

REQUESTS_VERSION=2.34.2
MATPLOTLIB_VERSION=3.11.1
PANDAS_VERSION=3.0.5
PYTORCH_VERSION=2.13.0

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

pyenv install 3.14.3
pyenv install 3.10.16

pyenv virtualenv 3.14.3 requests
pyenv virtualenv 3.14.3 matplotlib-pandas
pyenv virtualenv 3.10.16 pytorch

# requests setup: the requests source is not vendored in this repository; it is
# downloaded from the official GitHub repository at the pinned version and
# extracted to the same layout the config files expect.
if [ ! -d "requests/requests-${REQUESTS_VERSION}" ]; then
    mkdir -p requests
    curl -L -o "$tmp_dir/requests.tar.gz" "https://github.com/psf/requests/archive/refs/tags/v${REQUESTS_VERSION}.tar.gz"
    mkdir -p "requests/requests-${REQUESTS_VERSION}"
    tar xzf "$tmp_dir/requests.tar.gz" -C "requests/requests-${REQUESTS_VERSION}" --strip-components=1
fi
cd requests/requests-${REQUESTS_VERSION}
PYENV_VERSION=requests pyenv exec pip install -r requirements-dev.txt
PYENV_VERSION=requests pyenv exec pytest tests/test_utils.py

cd ../..
PYENV_VERSION=matplotlib-pandas pyenv exec pip install matplotlib==${MATPLOTLIB_VERSION} pandas==${PANDAS_VERSION}

# matplotlib setup: the image-comparison test fixtures (baseline_images) are not
# shipped with the installed matplotlib package; they are downloaded from the
# official matplotlib repository at the pinned version and copied into the
# installed package's tests/ directory.
if [ ! -d ~/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages/matplotlib/tests/baseline_images ]; then
    curl -L -o "$tmp_dir/matplotlib.tar.gz" "https://github.com/matplotlib/matplotlib/archive/refs/tags/v${MATPLOTLIB_VERSION}.tar.gz"
    tar xzf "$tmp_dir/matplotlib.tar.gz" -C "$tmp_dir" "matplotlib-${MATPLOTLIB_VERSION}/lib/matplotlib/tests/baseline_images"
    cp -r "$tmp_dir/matplotlib-${MATPLOTLIB_VERSION}/lib/matplotlib/tests/baseline_images" \
        ~/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages/matplotlib/tests/
fi
PYENV_VERSION=matplotlib-pandas pyenv exec pip install "pytest>=7.0.0"
PYENV_VERSION=matplotlib-pandas pyenv exec pytest ~/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages/matplotlib/tests/test_agg.py

# pandas setup
PYENV_VERSION=matplotlib-pandas pyenv exec pip install hypothesis tzdata
PYENV_VERSION=matplotlib-pandas pyenv exec pytest ~/.pyenv/versions/3.14.3/envs/matplotlib-pandas/lib/python3.14/site-packages/pandas/tests/indexes/multi/test_sorting.py

# pytorch setup
PYENV_VERSION=pytorch pyenv exec pip install torch==${PYTORCH_VERSION} pytest==9.1.1
PYENV_VERSION=pytorch pyenv exec pytest ~/.pyenv/versions/3.10.16/envs/pytorch/lib/python3.10/site-packages/torch/fx/passes/tests/test_pass_manager.py
