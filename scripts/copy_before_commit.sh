#!/bin/sh
# Copy dependencies file to the project cookiecutter template folder
cp .pre-commit-config-for-gen.yaml {{cookiecutter.project_slug}}/.pre-commit-config.yaml
cp poetry.lock {{cookiecutter.project_slug}}/poetry.lock
cp requirements.txt {{cookiecutter.project_slug}}/requirements.txt
cp .gitignore {{cookiecutter.project_slug}}/.gitignore

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
