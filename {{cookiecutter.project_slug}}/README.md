# {{cookiecutter.project_name}}

# Quick Start

## Install dependencies

### By pip

```bash
# Activate your virtualenv first is recommended
pip install -r requirements.txt
```

### By poetry
```bash
poetry env use /path/to/your/python/executable
poetry install
```

## Migrate database

**If you set `add_example_app` to `n`, you can skip this step and start by `django-admin startapp your_app`**

```bash
python manage.py makemigrations
python manage.py migrate
```

## Run system check

```bash
python manage.py check
```

## Run server
    
```bash
python manage.py runserver
```
