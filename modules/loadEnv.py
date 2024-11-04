# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/loadEnv.py
# Licensed under the GNU General Public License Version 3.0 (see below for more details)

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
            if argument in ["--env-file", "--help", "--version"]: continue
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
        envData = {
            "rbx_token": str(os.getenv("RBX_TOKEN")),
            "user_agent": str(os.getenv("USER_AGENT"))
        }
        return envData

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.