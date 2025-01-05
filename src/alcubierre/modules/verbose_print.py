# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/verbose_print.py
"""
Allows for the program to print out debug text,
but only when the user specifies for it.

I could've used logging. I should've used logging.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

import logging
import inspect

logger = logging.getLogger()

VERBOSE = False
vPrint = None
VERY_VERBOSE = False
vvPrint = None


def toggle_verbose_print():
    """
    Toggles verbose printing.
    """
    global VERBOSE
    VERBOSE = not VERBOSE
    # print(verbose)
    activate_lambda()


def toggle_very_verbose_print():
    """
    Toggles *very* verbose printing.
    """
    global VERY_VERBOSE
    VERY_VERBOSE = not VERY_VERBOSE
    # print(verbose)
    activate_lambda()


def log_n_print(message):
    """
    Logs and prints the message (debug level).

    It inspects the stack to get the module name
    and line number that called this function.
    """
    print(message)
    frm = inspect.stack()[1]
    log(message, frm)


def error_n_print(message):
    """
    Logs and prints the message (error level).

    It inspects the stack to get the module name
    and line number that called this function.
    """
    print(message)
    frm = inspect.stack()[1]
    log(message, frm, level=logging.ERROR)


def log(message, frm=None, level=logging.DEBUG):
    """
    Logs the string given to a file.

    It inspects the stack to get the module name
    and line number that called this function.
    """
    if frm is None:
        frm = inspect.stack()[1]

    mod = inspect.getmodule(frm[0])
    message = f"{mod.__name__}:{frm.lineno} - {message}"
    logger.log(level, message)


def activate_lambda():
    """
    Activates verbose/very verbose printing if the variables are True.
    """
    global vPrint
    global vvPrint
    vPrint = log_n_print if VERBOSE else log  # lambda *a, **k: None
    vvPrint = log_n_print if VERY_VERBOSE else log  # lambda *a, **k: None


activate_lambda()

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
