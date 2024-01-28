import secrets
from pathlib import Path

PROJECT_DIRECTORY = Path.cwd()

RANDOM_STRING_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

DJANGO_SECRET_KEY = "".join(secrets.choice(RANDOM_STRING_CHARS) for i in range(50))


def rm_tree(pth: Path):
    pth = pth if isinstance(pth, Path) else Path(pth)
    if not pth.exists():
        return
    for child in pth.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()


def remove_file(filepath: Path | str):
    filepath = PROJECT_DIRECTORY / Path(filepath)
    if filepath.exists():
        if filepath.is_dir():
            rm_tree(filepath)
        else:
            filepath.unlink(missing_ok=True)


def replace_secret_key():
    # replace SECRET_KEY in env/.env.base

    env_base = PROJECT_DIRECTORY / "env" / ".env.base"

    # print all files
    print("Files:")
    for f in PROJECT_DIRECTORY.glob("**/*"):
        print(f)

    with env_base.open("a") as f:
        f.write(f"\nSECRET_KEY={DJANGO_SECRET_KEY}\n")


if __name__ == "__main__":
    if "{{ cookiecutter.add_gh_workflow }}" != "y":
        remove_file(".github")
    elif "{{ cookiecutter.gh_workflow_publish_to_pypi }}" != "y":
        remove_file(".github/workflows/publish-pypi.yaml")

    if "{{ cookiecutter.add_pre_commit }}" != "y":
        remove_file(".pre-commit-config.yaml")

    if "{{ cookiecutter.add_example_app }}" != "y":
        remove_file("example_app")

    replace_secret_key()
