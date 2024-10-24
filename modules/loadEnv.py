# alcubierre
# ./modules/loadEnv.py
# Licensed under the GNU General Public License v3.0

import os, argparse, typing
from dotenv import load_dotenv

def createEnvTemplate(parser: argparse.ArgumentParser, env_file):
    """
    Create a template .env from the argparse arguments.
    HIGHLY EXPERIMENTAL AND NOT NEEDED! Currently, loading an .env file only accepts [rbx_token] and [user_agent].
    """
    with open(env_file, "w") as f:
        for argument in parser._option_string_actions:
            action = parser._option_string_actions[argument]
            if argument in ["--env-file", "--help", "--version"]:
                continue
            #print(argument)
            if argument.startswith("--"):
                env_var_name = argument[2:].replace("-", "_").upper()
                default_value = action.default if action.default is not argparse.SUPPRESS else ""
                f.write(f"# {action.help}\n")
                f.write(f"{env_var_name}={default_value}\n\n")

def loadEnvFile(envFile) -> typing.Dict[str,str]: # dict[str,str]: # # __future__.annotations can only do so much for compatibility
    # env_loaded = False
    if os.path.isfile(envFile):
        load_dotenv(envFile)
        envData = {"rbx_token": str(os.getenv("RBX_TOKEN")),
         "user_agent": str(os.getenv("USER_AGENT"))
        }
        return envData