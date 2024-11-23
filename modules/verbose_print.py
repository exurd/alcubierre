# alcubierre - Roblox Badge-to-Badge Place Teleporter
# ./modules/verbose_print.py
"""
Allows for the program to print out debug text,
but only when the user specifies for it.

I could've used logging. I should've used logging.
"""
# Licensed under the GNU General Public License Version 3.0
# (see below for more details)

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


def activate_lambda():
    """
    Activates verbose/very verbose printing if the variables are True.
    """
    global vPrint
    global vvPrint
    vPrint = print if VERBOSE else lambda *a, **k: None
    vvPrint = print if VERY_VERBOSE else lambda *a, **k: None


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
