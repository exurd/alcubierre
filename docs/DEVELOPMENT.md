## Create .conda enviroment(s) for multiple Python versions
> [!WARNING]  
> Older versions of Python that are not supported will contain vulnerabilities that will never get patched (as well as any required obsolete packages; e.g. `requests` and `python-dotenv`). If you're going to run alcubierre on an operating system that frequently gets updates, you will most likely be able to run supported versions of Python. The released binaries will always use the latest version of Python to compile.

> [!IMPORTANT]
> Currently, alcubierre can technically run on *Python 3.6* and above. *3.5* and below does not support f-strings. However, 3.9 is currently the lowest version that will install via pip. Please do not create a pull request that adds support below 3.5 ([#1](https://github.com/exurd/alcubierre/issues/1)).

To create a conda enviroment, you will need to [have conda installed](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). It's recommended to use miniconda if you're going to test multiple versions of Python with this code. The .conda folder has been .gitignored; use this folder to contain these enviroments.

Once properly installed, run this command in the terminal. Windows users need to use the Anaconda Prompt to run conda commands. Replace the stars with the version number you want.

```bash
cd /to/this/repo # c:\for\windows\
conda create -c conda-forge --prefix ./.conda/env3.* python=3.*
```

## Activating an .conda enviroment
You can use conda's way of activating an enviroment.

```bash
conda activate ./.conda/env3.13
```

When activating an enviroment for the first time, make sure to follow the install instructions in the README.md, mainly about installing the required packages.

> [!NOTE]
> If you are using VS Code, you can quickly select which interpreter to use. When switching enviroments, any opened terminals will still use the old enviroment, so make sure to close it to fully switch. You can run `python --version` to check if the enviroments successfully changed.

## Creating binary executables with PyInstaller
PyInstaller can be used to create an easy to use version of this program. Public releases on GitHub will always use the latest stable version of Python to create binaries. PyInstaller is not included in requirements.txt; manually install it with `pip install pyinstaller`

Example commands:
```bash
# conda 3.13 environment, in root directory of repo
pyinstaller --name=alcubierre --add-data="sounds:sounds" --icon="docs/icon.ico" __main__.py

# to make a one file version of this program, add --onefile
pyinstaller --onefile --name=alcubierre --add-data="sounds:sounds" --icon="docs/icon.ico" __main__.py
```

You will need to add the "[sounds](/sounds)" folder with `--add-data` (shown in the above examples).

An icon is available in [./docs/icon.ico](icon.ico) and can be included with the `--icon`.

`--optimize=2` sets the [Bytecode Optimization Level](https://pyinstaller.org/en/v6.6.0/feature-notes.html#bytecode-optimization-level) to 2, which removes docstrings and assert statements. Not recommended, as it will disable Tracebacks.

Linux (and MacOS systems with the [Xcode Command Line Tools](https://stackoverflow.com/q/9329243)) can use `--strip` to further shrink the filesize.

To create a .spec file, use the same command but replace `pyinstaller` with `pyi-makespec`. To use the .spec file you cr, run `pyinstaller alcubierre.spec`.

### MacOS specific options for building universal2 binaries
If you want to build an executable that can run on both Apple Silicon and Intel, you will need universal2 Python from [python.org/downloads](https://www.python.org/downloads/). 

As of November 2024, **you cannot use conda or homebrew python installs to create universal2 binaries!** It is highly recommended to create a virtual enviroment through venv for the universal2 Python install.

When installing requirements.txt, you need to run `pip install --no-binary :all: -r requirements.txt`. This creates universal2 compatible modules. Skipping this step or installing it the normal way will cause `PyInstaller.utils.osx.IncompatibleBinaryArchError`.

Once prepared correctly, include `--target-arch universal2` in the pyinstaller command.

## .gitignores

There are multiple folders that have been ignored in git: `alcubierre_cache`, `textFiles`, `.envs`. It is advised to use those folders to avoid cluttering the repository and/or leaking sensitive info.

> [!CAUTION]  
> If you accidentally push a commit containing your .ROBLOSECURITY cookie, consider it compromised and *refresh your token as soon as possible!* You can refresh the token by logging out of the session you grabbed the token from (consider also using the option to log out of all devices).
> Even if the branch with the commit is deleted, GitHub stores pull request commits (as a hash) to the repository and any forks created afterwards. More info can be found on GitHub Docs: "[Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)"

## Pull Requests
> [!TIP]
> Please sign your commits, through SSH or GPG. Learn more on GitHub Docs: "[About commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification)"

As said before, please do not create a pull request that adds support below Python 3.5 ([#1](https://github.com/exurd/alcubierre/issues/1)).