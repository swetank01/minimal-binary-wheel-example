# minimal-binary-wheel-example

A simple example demonstrating the bare essentials needed for binary-compiling
Python code to create a standard Python wheel package.

**Table of Contents**

* [About](#about)
* [Initial repo installation and configuration](#initial-repo-installation-and-configuration)
* [Usage](#usage)
    * [About the Flask app](#about-the-flask-app)
    * [Compiling and packaging](#compiling-and-packaging)
    * [Testing the built wheel](#testing-the-built-wheel)
    * [Inspecting the built wheel](#inspecting-the-built-wheel)
* [Implications of binary distributions vs source distributions](#implications-of-binary-distributions-vs-source-distributions)
* [Building Linux wheels in a ManyLinux container](#building-linux-wheels-in-a-manylinux-container)
* [Troubleshooting tips and techniques](#troubleshooting-tips-and-techniques)
* [Further detail](#further-detail)


## About

The very simple use case here is to compile (and thus protect) the source code
for a "Hello, World" Flask app, while still preserving all functionality.

The high-level summary of the approach in this example is:

1. Use Nuitka to compile Python code down to a platform-specific binary (`.so`
   for Linux/MacOS, `.pyd` for Windows)
2. Use `stubgen` (from the `mypy` package) to create `.pyi` files for all
   relevant modules (helps with autocompletion, parameter hinting, etc)
3. Use Poetry to create a Python wheel package, ensuring that we do not include
   any undesired repository files in the resulting Python package.


## Initial repo installation and configuration

You must first install and configure `poetry`: https://python-poetry.org/docs/#installation

Recommended Poetry configuration:

```bash
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true
```

You can then create the virtual environment and install dependencies:

```bash
poetry install
```


## Usage

All of the below sections assume that your virtual environment is activated:
`poetry shell`


### About the Flask app

This very simple Flask app can be run from a Python shell as follows:

```python
from binary_wheel_example import app
app.run()
```


### Compiling and packaging

This example uses `invoke` to automate the process of compiling and packaging
the wheel:

```bash
invoke build
```

The output of the above `invoke` task will be a `.whl` file in the current
directory that is compiled and tagged for the operating system and Python
version used to call `invoke`.

### Testing the built wheel

For the sake of example, let's assume we ran the above commands on a Linux
system using Python 3.8. In a new directory (to make sure we're performing a
clean test away from the original source code), do the following:

```bash
# Create a virtual environment to install the wheel into
python3.8 -m venv .venv
source .venv/bin/activate

# Install the wheel
pip install path/to/your-wheel-filename.whl

# Confirm that the Flask app works
python -c 'from binary_wheel_example import app; app.run()'
```


### Inspecting the built wheel

A Python wheel is just a Zip file with a particular required file structure. It
is highly recommended to inspect the built wheel to ensure that no undesired
files have been inadvertently included in the package:

```bash
unzip [FILENAME].whl
```

> **Tip:** Some editors (Emacs, recent versions of Neovim) have the ability to
> directly browse a zip file's contents. For Vim variants, you probably want
> the following in your `.vimrc` (or similar) config so that it treats `.whl`
> files as `.zip` files:
>
> ```
> autocmd BufReadCmd *.whl call zip#Browse(expand("<amatch>"))
> ```


## Implications of binary distributions vs source distributions

Because we are compiling the source code to platform-specific binaries, we can
no longer leverage the cross-platform capabilities of a Python source-based
wheel; the binary extensions inside the `.whl` file will depend on certain
versions of OS libraries (e.g. `GLIBC` for Linux binaries) to be present on the
target machine where the wheel is being installed.

This has the following implications:

1. We must compile and package a wheel for each OS, and for each Python version
   on that OS that we want to support. i.e. if you want to support Python 3.8,
   3.9, and 3.10 on Windows and Linux, that's 3 Python versions * 2 Operating
   Systems = 6 wheels we need to build, for each version of our software.
2. Publishing a version of our software to e.g. PyPI.org means publishing all
   wheels for that particular version. Thankfully, `twine` makes this easy with
   `twine upload *.whl`.
3. Installing our software means that the specific wheel matching our platform
   and must be selected. `pip` will handle selection of the wheel automatically
   (see [Python compatibility
   tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#platform-compatibility-tags)
   for more on how this is done).

## Building Linux wheels in a ManyLinux container

When buildling Linux wheels, it is strongly advised to perform compilation and
packaging inside of a [ManyLinux container](https://github.com/pypa/manylinux).
ManyLinux images are specially crafted for maximum Linux OS compatability when
it comes to OS-level dependencies (such as the aforementioned `GLIBC`).


## Troubleshooting tips and techniques

One of the more common problems you will run into with binary wheels is that
`pip install` will complain that...

- A particular wheel is not compatible with the target platform when running
  `pip install [FILENAME].whl`, or
- There are no compatible wheels found for the target platform.

Both issues ultimately stem from the fact that `pip` uses information about
your system to search for a wheel with matching  arch, Python version, and ABI
tags (see the [Python compatibility
tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/#platform-compatibility-tags)
page). When `pip` cannot find any wheels for your package with arch/ABI/Python
version tags supported by your system, you will see errors like this.

The typical approach to solving these types of issues is:

1. Try upgrading `pip` in the target installation environment via `pip install
   -U pip`; sometimes this is all you need.
2. Get detailed information about what `pip` thinks is supported in the target
   environment by running `pip debug info --verbose`. This will list all of the
   supported compatibility tags that a wheel can have, in order to be installed
   in that environment.

## Further detail

- See comments in `pyproject.toml` for a detailed explanation of the Poetry
  project configuration needed.
- See comments in `tasks.py` for the `invoke` automation around compiling to
  binary and packaging the wheel.
