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
boto_config_info = None


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

def create_boto_client_using(credential: str, is_role=False):
    """ TODO: add docstring for function
    """
    # If the user passed a role
    if is_role:
        pass

    # If user passed object or aws profile
    else:
        pass


def get_current_account_id() -> str:
    """Gets the alias of the AWS account that's created the IAM client or returns account number

    :param None

    :returns: The alias or account number of the AWS account inspected by the tool
    :rtype: str
    """
    global iam_client
    global boto_config_info

    # blank alias holder
    alias_holder = []

    # Get list of aliases used for client
    alias_paginator = iam_client.get_paginator('list_account_aliases')

    for response in paginator.paginate():
        alias_holder.append(response['AccountAliases'])
    
    # Assumption is made that the alias of the first index in list is correct
    if len(alias_holder) > 0:
        # Make sure 'AccountAliases' list is not empty and return
        if alias_holder[0]:
            return alias_holder[0]
        else:
            # Check to see if boto_config_info has a value set, which will assume 
            # that either a role, profile, or credential object was passed.
            if boto_config_info != None:
                try:
                    # Use boto_config_info to build STS client and retrieve the account number.
                    account_number = boto_config_info.client('sts').get_caller_identity().get('Account')
                except:
                    # TODO: Create more specific exception handlers with actions
                    return "N/A - GET ACC FAIL"
                else:
                    return account_number

def are_set_credentials_arguments_active(arguments) -> None:
    """Checks the arguments passed and sees if any AWS credential overrides are present

    :param arguments: The arguments passed into script
    :type: :class:`argparse.Namespace`

    :returns: None
    """
    global account_identification

    if arguments.use_aws_profile or arguments.use_credential_as_object:
        credential_value = ""
        if arguments.use_credential_as_object:
            credential_value = arguments.use_credential_as_object
        else:
            credential_value = arguments.use_aws_profile
        # Create boto client using argument
        create_boto_client_using(credential_value, is_role=False)

    elif arguments.use_aws_role:
        # Create boto client using argument
        create_boto_client_using(arguments.use_aws_role, is_role=True)

    # Get the alias and set to global variable
    account_identification = get_current_account_id()



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
        help="Use this to tell the tool which of your profiles from your AWS credential file on your local machine to use",
        default="default"
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

    # Check to see the method the user wishes to authenticate/ create their boto client
    are_set_credentials_arguments_active(args)