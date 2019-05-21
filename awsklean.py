#! /usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import botocore
import sys
import os
import argparse
import ast
import json
import requests



# GLOBAL SCRIPT VARIABLES
script_location = os.path.dirname(os.path.realpath(__file__))
script_version = "0.0.1"
script_name = sys.argv[0].strip(".py")
is_dry_run_mode_set = False
is_notify_slack_mode_set = False
account_identification = None


def is_dry_run_active(state: bool) -> None:
    """Checks to see if --dry-run argument is passed to the script and sets global variable accordingly


    :param state: Whether --dry-run was passed as argument
    :type state: bool

    :returns: None
    """
    global is_dry_run_mode_set

    is_dry_run_mode_set = state


def is_notify_slack_active(state: bool) -> None:
    """Checks to see if --slack-notify argument is passed to the script and sets global variable accordingly


    :param state: Whether --slack-notify was passed as argument
    :type state: bool

    :returns: None
    """
    global is_notify_slack_mode_set

    is_notify_slack_mode_set = state


def should_show_version(passed: bool) -> None:
    """Prints the tool's version number to the terminal and exits tool


    :param passed: Whether --version argument was passed
    :type passed: bool

    :returns: None
    """
    if passed:
        print(f"{script_name} version {script_version}")
        exit()

def send_to_slack_this(message: str) -> None:
    """Sends message to specified webhook that's saved as an environment variable

    :param message: Message to send to Slack channel
    :type message: str
    :raises: :class:`KeyError`: Cannot find environment variable for AWSKLEAN_SLACK_WEBHOOK


    :returns: None
    """
    try:
        slack_webhook = os.environ["AWSKLEAN_SLACK_WEBHOOK"]
    except KeyError:
        print("""Unable to detect an environmental variable with the name AWSKLEAN_SLACK_WEBHOOK, Please
set this before passing the --notify-slack argument.
        """)
        exit()
    
    # Build valid dict containing message and configuration
    configured_message_dict = ast.literal_eval(
        f"""{{ "text": "{message}", "icon_url": "https://www.freeiconspng.com/uploads/black-key-symbol-icon-6.png", "username": "{script_name[:4].upper() + script_name[4:].lower()}"}}"""
    )

    # Send POST request to webhook containing message
    requests.post(
        slack_webhook,
        data = json.dumps(configured_message_dict)
    )


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_group = argument_parser.add_mutually_exclusive_group()

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

    argument_parser.add_argument(
        "--notify-slack",
        help="Use to send notification(s) back to slack channel using webhook (Soon to be deprecated)",
        action="store_true"
    )

    argument_group.add_argument(
        "-ucao",
        "--use-credential-as-object",
        help="Use this to pass an object with AWS access key credentials"
    )

    argument_group.add_argument(
        "-uap",
        "--use-aws-profile",
        help="Use this to tell the tool which of your profiles from your AWS credential file on your local machine to use"
    )

    argument_group.add_argument(
        "-uar",
        "--use-aws-role",
        help="Use this to pass in the AWS account number and role name (as a comma-separated string) to be used"
    )

    args = argument_parser.parse_args()

    # Action if version argument(s) passed
    should_show_version(args.version)

    # Update global variable if dry-run passed
    is_dry_run_active(args.dry_run)

    # Update global variable if notify-slack passed
    is_notify_slack_active(args.notify_slack)