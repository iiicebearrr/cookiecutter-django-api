#!/bin/sh
# this is a very simple script that tests the docker configuration for cookiecutter-django
# it is meant to be run from the root directory of the repository, eg:
# sh tests/test_bare.sh

set -o errexit
set -x

# Copy dependencies file to the project cookiecutter template folder
cp .pre-commit-config-for-gen.yaml {{cookiecutter.project_slug}}/.pre-commit-config.yaml
cp poetry.lock {{cookiecutter.project_slug}}/poetry.lock
cp requirements.txt {{cookiecutter.project_slug}}/requirements.txt

rm -f {{cookiecutter.project_slug}}/pyproject.toml

awk '/^\[tool.poetry\]/ {flag=1; next} /^\[/ {flag=0} !flag' pyproject.toml >{{cookiecutter.project_slug}}/pyproject.toml

sed -i '' '1i\
[tool.poetry]\
name = "{{cookiecutter.project_slug}}"\
version = "{{cookiecutter.version}}"\
description = "{{cookiecutter.description}}"\
authors = ["{{cookiecutter.author_name}} <{{cookiecutter.author_email}}>"]\
readme = "README.md"\
packages = [{ include = "{{cookiecutter.project_slug}}" }]


' {{cookiecutter.project_slug}}/pyproject.toml
# create a cache directory
mkdir -p .cache/bare
cd .cache/bare

cookiecutter ../../ --no-input --overwrite-if-exists "$@"

cd my_django_project

# Install Python deps
pip install -r requirements.txt

# Make sure the check doesn't raise any warnings
python manage.py check --fail-level WARNING
