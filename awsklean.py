#! /usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import botocore
import sys
import os
import argparse



# GLOBAL SCRIPT VARIABLES
script_location = os.path.dirname(os.path.realpath(__file__))
script_version = "0.0.1"
script_name = sys.argv[0].strip(".py")
is_dry_run_mode_set = False


def is_dry_run_active(state: bool) -> None:
    """Checks to see if --dry-run argument is passed to the script and sets global variable accordingly


    :param state: Whether --dry-run was passed as argument
    :type state: bool

    :returns: None
    """
    global is_dry_run_mode_set

    is_dry_run_mode_set = state


def should_show_version(passed: bool):
    """Prints the tool's version number to the terminal and exits tool


    :param passed: Whether --version argument was passed
    :type passed: bool

    :returns: None
    :rtype: None
    """
    if passed:
        print(f"{script_name} version {script_version}")
        exit()


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        "-v",
        "--version",
        help="Use to check the version of the tool",
        action="store_true"
    )

    argument_parser.add_argument(
        "--dry-run",
        help="Use to check what actions would be carried out upon execution of passed arguments",
        action="store_true"
    )

    args = argument_parser.parse_args()

    # Check if version argument(s) passed
    should_show_version(args.version)

    # Check to see if dry-run passed
    is_dry_run_active(args.dry_run)