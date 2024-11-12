## Create .conda enviroment(s) for multiple Python versions
> [!WARNING]  
> Older versions of Python that are not supported will contain vulnerabilities that will never get patched (as well as any required obsolete packages; e.g. `requests` and `python-dotenv`). If you're going to run alcubierre on an operating system that frequently gets updates, you will most likely be able to run supported versions of Python. The released binaries will always use the latest version of Python to compile.

> [!IMPORTANT]
> Currently, alcubierre can run on *Python 3.6* and above. *3.5* and below does not support f-strings. 3.6 will be the lowest version this script will try and support. Please do not create a pull request that adds support below 3.5 ([#1](https://github.com/exurd/alcubierre/issues/1)).

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

## Creating binary files
PyInstaller can be used to create a binary version of this program.

```bash
# in conda 3.13 enviroment, root repo directory:
pyinstaller --optimize=2 --name=alcubierre --add-data="sounds:sounds" --icon="docs/icon.ico" __main__.py
```

For one file:
```bash
# in conda 3.13 enviroment, root repo directory:
pyinstaller --onefile --optimize=2 --name=alcubierre --add-data="sounds:sounds" --icon="docs/icon.ico" __main__.py
```

## .gitignores

There are multiple folders that have been ignored in git: `alcubierre_cache`, `textFiles`, `.envs`. It is advised to use those folders to avoid cluttering the repository and/or leaking sensitive info.

> [!CAUTION]  
> If you accidentally push a commit containing your .ROBLOSECURITY cookie, consider it compromised and *refresh your token as soon as possible!* You can refresh the token by logging out of the session you grabbed the token from (consider also using the option to log out of all devices).
> Even if the branch with the commit is deleted, GitHub stores pull request commits (as a hash) to the repository and any forks created afterwards. More info can be found on GitHub Docs: "[Removing sensitive data from a repository](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)"

## Pull Requests
> [!TIP]
> Please sign your commits, through SSH or GPG. Learn more on GitHub Docs: "[About commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification)"

As said before, please do not create a pull request that adds support below Python 3.5 ([#1](https://github.com/exurd/alcubierre/issues/1)).