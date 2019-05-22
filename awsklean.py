#! /usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import botocore
from botocore.exceptions import ProfileNotFound
import sys
import os
import argparse
import ast
import collections
import json
import requests
import random
import time
import datetime
from dateutil.tz import tzutc
import dateutil.parser


                                                                                                                                                                                                                                                              

# GLOBAL SCRIPT VARIABLES
script_location = os.path.dirname(os.path.realpath(__file__))
script_version = "0.0.1"
script_name = sys.argv[0].strip(".py")
is_dry_run_mode_set = False
is_notify_slack_mode_set = False
account_identification = None
boto_config_info = None
iam_client = None
list_of_users_to_action = collections.defaultdict(dict)


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

# Generate random number
def generate_random_number_between(first: int =  1, last: int = 101) -> int:
    """Generates a number between the first and last integers


    :param first: Start of generation range
    :type first: int
    :param last: End of generation range
    :type last: int

    :returns: Randomly generated int
    :rtype: int
    """
    return random.randint(first, last)

def create_boto_client_using(credential: str, is_role: bool = False, session_token: str = "") -> None:
    """Uses the passed credentials and attempts to create a boto client with it


    :param credentials: Desired credentials as a plain, comma-separated, or object like string
    :type credentials: str
    :param is_role: Whether the passed credentials is a role type credential
    :type is_role: bool
    :param session_token: Token provide when using an assumed role
    :type str


    :returns: None
    """
    global iam_client
    global boto_config_info

    # If the user passed a role
    if is_role:
        # Check to make sure credentials is comma-seperated
        if ',' not in credential:
            print("\nPlease ensure you are passing the role using a comma-seperated string.\n Use `python {script_name}.py --help` for more information")
            exit()
        
        # Attempt to use available leading AWS to create STS client
        try:
            sts_client = boto_config_info.client('sts')
        except:
            sts_client = boto3.client('sts')
        
        # Create account number and role name variables
        aws_account_number_for_role, name_of_role = credential.split(",")

        # Attempt to assume role
        try:
            assumed_role_object = sts_client.assume_role(
                RoleArn = f"arn:aws:iam::{aws_account_number_for_role}:role/{name_of_role}",
                RoleSessionName=f"AssumeRoleSession{generate_random_number_between()}"
            )
        except botocore.exceptions.ClientError as e:
            # Will raise if role assumption fails
            print(e)
            print("""ATTENTION:
The base lead account used (default) does not have permissions to carry out Role Assumption using, AWS STS.
Please update its Policy to include the AWS IAM service.
""")
            exit()
        else:
            # Get credential from returned object
            credential = assumed_role_object['Credentials']

            # Temporary variables to hold assumed credential
            tmp_access_key_id, tmp_secret_access_key, tmp_session_token = credential['AccessKeyId'], credential['SecretAccessKey'], credential['SessionToken']
            
            # Use temporary variables to create IAM client
            tmp_credential_str_object = f"{{ 'aws_key_id': '{tmp_access_key_id}', 'aws_secret': '{tmp_secret_access_key}' }}"
            create_boto_client_using( credential=tmp_credential_str_object, 
                                        is_role=False, 
                                        session_token=tmp_session_token
                                    )

    # If user passed object or aws profile name
    else:

        # Look for curly brace in credential as this is a unique attribute of credential string object
        if "{" in credential:
            # Attempt to convert string object to valid dict
            try:
                credential = ast.literal_eval(credential)
            except ValueError:
                print("""ATTENTION:
Ensure you are using the correct format when attempting to pass a
AWS credential object. It must look like the following:

"{{ 'aws_key_id': '<INSERT_AWS_KEY_HERE>', 'aws_secret': '<INSERT_AWS_SECRET_HERE>' }}" 

IMPORTANT:
    • Please note the use of single and double quotes!
""")
                exit()

        # If conversation took place and successful
        if isinstance(credential, dict):
            # Check to see if session token not passed
            if not session_token:
                # Create crrent session using dict and assign to global variable
                current_session = boto3.session.Session(aws_access_key_id=credential['aws_key_id'], aws_secret_access_key=credential['aws_secret'])
                boto_config_info = current_session
            else:
                # Create crrent session using dict AND session token, them assign to global variable
                current_session = boto3.session.Session(aws_access_key_id=credential['aws_key_id'], aws_secret_access_key=credential['aws_secret'], aws_session_token=session_token)
                boto_config_info = current_session
            
            print(f"{script_name} is connecting using a credential object")

            # Create IAM client using session created above
            iam_client = current_session.client("iam")
        
        # look to see if credential passed a string
        elif isinstance(credential, str):
            # Assume the credential pass is set up in the aws credential config file
            # AND create a session, them assign to global variable 
            try:
                current_session = boto3.session.Session(profile_name=credential)
                boto_config_info = current_session

                # Create IAM client
                iam_client = current_session.client("iam")
            except ProfileNotFound:
                # Will raise if profile cannot be found
                print(f"""ATTENTION: \nThe profile "{credential}" does not appear to be present in the AWS credentials config file. \nOn Unix systems, this often can be found in the ~/.aws directory. \nPlease double-check and add if necessary!""")
                exit()
        
        else:
            # Use default AWS credential
            iam_client = boto3.client('iam')

def get_current_account_id() -> str:
    """Gets the alias of the AWS account that has created the IAM client or returns account number

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

    for response in alias_paginator.paginate():
        alias_holder.append(response['AccountAliases'])
    
    # Assumption is made that the alias of the first index in list is correct
    if len(alias_holder) > 0:
        # Make sure 'AccountAliases' list is not empty and return first index
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

def get_all_users_in_aws_account():
    """Uses global IAM client to generate a list of all the users in the account with their
    user account information

    :param None

    :returns: List of user accounts and account information. A row per user.
    :rtype: list
    """
    seconds_to_wait = 5

    # Generate IAM user report
    response = iam_client.generate_credential_report()

    # Attempt to get report
    try:
        response = iam_client.get_credential_report()
    except iam_client.exceptions.CredentialReportNotReadyException:
        print(f"""ATTENTION:\nGathering information for all users, please wait.  The process will take approximately {seconds_to_wait} seconds.""")
        time.sleep(seconds_to_wait)
        try:
            response = iam_client.get_credential_report()
        except iam_client.exceptions.CredentialReportNotReadyException:
            print(f"""ATTENTION:\nSomething has gone wrong, please try again in around {seconds_to_wait} minutes""")
            exit()
    
    # Return a list with the information about all the users from report
    return response['Content'].decode().split('\n')

def convert_this_to_date(string: str = "") -> object:
    """Converts passed string to a date object

    :param string: Date written as string
    :type string: str

    :returns: Date object
    :rtype object
    """
    return dateutil.parser.parse(string)  

def get_all_users_not_used_in_the_last(number_of_days: int = 60, source_report: list = get_all_users_in_aws_account, display=False):
    """Checks to see if any user accounts in the source report have not logged in AWS in specified time.

    :param days: The number of days before today to check up until
    :type days: int
    :param source_report: List of the AWS IAM accounts to check
    :type list
    :param display: Whether function should output to the terminal or return list

    :returns: List of user objects that are unused within the specified time
    """

    number_of_days_as_delta = datetime.timedelta(days=number_of_days)

    # Get current date/time in the same timezone used by AWS system
    current_date_tzutc = datetime.datetime.now(tzutc())

    # List to hold users who have not been used in specified time
    list_of_all_aws_users_out_of_range = []

    for user in source_report()[1:]:
        user = user.split(",")

        try:
            # Check if password_enabled is set to 'true'
            if user[3] == 'true':
                # Check to see if there is any information on the last time password was used
                if user[4] == 'no_information':
                    # Make sure user is not super user before adding to list
                    # if user[0] not in list_of_superUs['SuperUser']:
                    list_of_users_to_action[user[0]]['password_access'] = 'null'
                # Check if password_last_used is older than the specificed range        
                elif convert_this_to_date( string = user[4] ) < (current_date_tzutc - number_of_days_as_delta):
                    # Make sure user is not super user before adding to list
                    # if user[0] not in list_of_superUs['SuperUser']:
                    list_of_all_aws_users_out_of_range.append(user)
                    list_of_users_to_action[user[0]]['password_access'] = True
                else:
                    # Make sure user is not super user before adding to list
                    # if user[0] not in list_of_superUs['SuperUser']:
                    list_of_users_to_action[user[0]]['password_access'] = False
            else:
                # Make sure user is not super user before adding to list
                # if user[0] not in list_of_superUs['SuperUser']:
                list_of_users_to_action[user[0]]['password_access'] = 'null'
            # Check if access_key_1_active is set to 'true'
            if user[8] == 'true':
                # Check to see if access_key_last_used_date is NOT 'N/A'
                if user[10] != 'N/A':
                    # Check to see if access_key_last_used_date is 'no_information'
                    if user[10] == 'no_information':
                        # if user[0] not in list_of_superUs['SuperUser']:
                        list_of_users_to_action[user[0]]['access_key_1_access'] = True
                    # Check if access_key_1_last_used_date is older than the specificed range
                    elif convert_this_to_date( string = user[10] ) < (current_date_tzutc - number_of_days_as_delta):
                        # Make sure user is not super user before adding to list
                        # if user[0] not in list_of_superUs['SuperUser']:
                        list_of_all_aws_users_out_of_range.append(user)
                        list_of_users_to_action[user[0]]['access_key_1_access'] = True
                    else:
                        # Make sure user is not super user before adding to list
                        # if user[0] not in list_of_superUs['SuperUser']:
                        list_of_users_to_action[user[0]]['access_key_1_access'] = False
                else:
                    # Make sure user is not super user before adding to list
                    # if user[0] not in list_of_superUs['SuperUser']:
                    list_of_users_to_action[user[0]]['access_key_1_access'] = True
            else:
                # Make sure user is not super user before adding to list
                # if user[0] not in list_of_superUs['SuperUser']:
                list_of_users_to_action[user[0]]['access_key_1_access'] = 'null'

            # Check if access_key_2_active is set to 'true'
            if user[13] == 'true':
                # Check to see if access_key_2_last_used_date is NOT 'N/A'
                if user[15] != 'N/A':
                    # Check to see if access_key_2_last_used_date is 'no_information'
                    if user[15] == 'no_information':
                        # if user[0] not in list_of_superUs['SuperUser']:
                        list_of_users_to_action[user[0]]['access_key_2_access'] = True
                    # Check if access_key_2_last_used_date is older than the specificed range
                    elif convert_this_to_date( string = user[15] ) < (current_date_tzutc - number_of_days_as_delta):
                        # Make sure user is not super user before adding to list
                        # if user[0] not in list_of_superUs['SuperUser']:
                        list_of_all_aws_users_out_of_range.append(user)
                        list_of_users_to_action[user[0]]['access_key_2_access'] = True
                    else:
                        # Make sure user is not super user before adding to list
                        # if user[0] not in list_of_superUs['SuperUser']:
                        list_of_users_to_action[user[0]]['access_key_2_access'] = False
                else:
                    # Make sure user is not super user before adding to list
                    # if user[0] not in list_of_superUs['SuperUser']:
                    list_of_users_to_action[user[0]]['access_key_2_access'] = True
            else:
                # Make sure user is not super user before adding to list
                # if user[0] not in list_of_superUs['SuperUser']:
                list_of_users_to_action[user[0]]['access_key_2_access'] = 'null'
        except KeyError as identifier:
            # TODO: Create more specific actions
            pass

    if display:
        # Print the list of users to terminal
        print(json.dumps(list_of_users_to_action, indent=4, separators=(',', ': ')))
    else:
        # Return list
        return list_of_users_to_action

def are_set_credentials_arguments_active(arguments: object) -> None:
    """Checks the arguments passed and sees if any AWS credential overrides are present

    :param arguments: The arguments passed into script
    :type: object

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

def initialise_leading_iam_client_check(arguments: object) -> None:
    """Checks the environemt variables to see if on a Jenkins manchine and sees if 
    expected arguments are passed if true. Otherwise creates leading IAM client with
    default aws credentials from aws cli

    :param arguments: The arguments passed into script
    :type: object

    :returns: None
    """
    global iam_client

    if os.getenv("JENKINS_URL") != None:
        # Makre sure user has passed the name of the AWS profile to use on Jenkins
        if args.jenkins_aws_profile_name:
            create_boto_client_using(credential=args.jenkins_aws_profile_name)
        else:
            print(f"""ATTENTION:
{script_name} has detected it is being used in a Jenkins system without you declaring which profile it should use by passing either one  of the `--jenkins-aws-profile-name`  OR `-japn` arguments. 

Please pass the argument with a valid profile name and try again!
""")
        
    else:
        # create placeholder for boto IAM client  
        iam_client = boto3.client('iam')

def check_and_action_active(arguments: object) -> None:
    """Checks the arguments passed to see which combination of functions need to be called and 
    forward the variables passed to the said function(s).

    :param arguments: The arguments passed into script
    :type: object

    :returns: None
    """
    if arguments.show_users_with_no_usage_within:
        get_all_users_not_used_in_the_last(number_of_days=arguments.show_users_with_no_usage_within, display=True)

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

    argument_parser.add_argument(
        "-japn",
        "--jenkins-aws-profile-name",
        help="Use to specify the profile name to use as default when on Jenkins",
    )

    argument_parser.add_argument(
        "-suwnuw",
        "--show-users-with-no-usage-within",
        help="Use this argument to show information on ALL users in the AWS account outlining any service for each user that has NOT had any usage within the specified number of days (with True), or False otherwise.",
        default = 60,
        type=int
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

    # Initialise IAM client using default profile if local or specified jenkins profile if on jenkins
    initialise_leading_iam_client_check(args)

    # Check to see the method the user wishes to authenticate/ create their boto client
    are_set_credentials_arguments_active(args)

    # Check to see what arguments have been passed and require specific action
    check_and_action_active(args)