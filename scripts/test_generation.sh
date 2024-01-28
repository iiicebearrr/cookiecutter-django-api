#!/bin/sh
# this is a very simple script that tests the docker configuration for cookiecutter-django
# it is meant to be run from the root directory of the repository, eg:
# sh tests/test_bare.sh

set -o errexit
set -x

bash scripts/copy_before_commit.sh

# create a cache directory
mkdir -p .cache/bare
cd .cache/bare

cookiecutter ../../ --no-input --overwrite-if-exists "$@"

cd my_django_project

# Install Python deps
pip install -r requirements.txt

# Make sure the check doesn't raise any warnings
python manage.py check --fail-level WARNING
