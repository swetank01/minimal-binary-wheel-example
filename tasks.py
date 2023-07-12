import shutil
from pathlib import Path

from invoke import task

PACKAGE_NAME = "binary_wheel_example"


@task()
def compile(c):
    """
    Compiles Python source down to a platform-specific binary.

    Note that we configure Nuitka to avoid creating a .pyi file. This is
    because Nuitka .pyi files are not as fully-featured as what can be created
    with e.g. `stubgen`, sd we leave this to a separate task.
    """
    c.run(
        f"python -m nuitka {PACKAGE_NAME} \
                 --module \
                 --no-pyi-file \
                 --include-package={PACKAGE_NAME}"
    )


@task()
def generate_interfaces(c):
    """
    Generate .pyi file(s) for applicable modules.
    """
    c.run("stubgen binary_wheel_example -o .")


@task(
    pre=[compile, generate_interfaces],
)
def build(c):
    """
    Run all tasks needed to compile Python source and produce a .whl file.
    """
    c.run("poetry build -f wheel")

    built_wheels = list(Path("dist").glob("*.whl"))
    for wheel_file in built_wheels:
        shutil.copy2(wheel_file, Path())
