import re
import sys

AUTHOR_PATTERN = re.compile(r"^(?:[- .,\w\d'’\"():&]+)(?: <(?:.+?)>)?")
MODULE_PATTERN = re.compile(r"^[_a-zA-Z][_a-zA-Z0-9]+$")

module_name = "{{ cookiecutter.project_slug}}"
author = '"{{ cookiecutter.author_name}} <{{ cookiecutter.author_email}}>"'

if not MODULE_PATTERN.match(module_name):
    print(
        "ERROR: The project slug (%s) is not a valid Python module name. Please do not use a - and use _ instead"
        % module_name
    )

    # Exit to cancel project
    sys.exit(1)

if not AUTHOR_PATTERN.match(author):
    print(
        "ERROR: The author name (%s) is not a valid author name. Please use a valid name"
        % author
    )

    # Exit to cancel project
    sys.exit(1)
