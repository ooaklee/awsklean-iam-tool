# AWSKlean - IAM Tool

## SUMMARY
`AWSKlean` is a Python script created to be used as a simple way to manage IAM users on Amazon Web Services (AWS) accounts.
It gives the user the ability to disable, and remove accounts (W.I.P) if they are unused over a specified time frame. 

## REQUIREMENTS
This script requires the following to have core functionality:
* Python 3.6+ (with modules installed)
* AWS IAM profile with `Full Access` on IAM service and ...(MORE TO BE ADDED) - WIP example will be added to the repo


## `ENVIRONMENT VARIABLES`
* AWSKLEAN_SLACK_WEBHOOK
* JENKINS_URL
* AWS_DEFAULT_REGION
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY


## FEATURES
Features include:
- **Tested with Python versions 3.6** 
- Allows user to get information about the last time access methods (Access Key(s) and Console access) are used on their AWS
- Allows user to disable account methods for IAM users that haven't been used within a specified time
-  awsklean provides notification via. Slack if webhook provided
- Gives a micro-report for each user on AWS account, outlining whether access method has NOT been used in specified time.

## INSTALLING REQUIREMENT

Install the tool's requirements by navigating to root directory  of repo and running: `pip install -r requirements.txt`

I often use a virtual environment, more information about setting up a virtual environment can be found [HERE](https://realpython.com/python-virtual-environments-a-primer/)

## USAGE

### `GETTING TOOL MAN PAGE`
To get information on what arguments the tools can take 
``` bash
    python awsklean.py --help
```

**OUTPUT** (AWSKlean version 1.0.2):
```
usage: awsklean.py [-h] [-v] [--dry-run] [--notify-slack]
                   [-suu SUPER_USERS_URL] [-japn JENKINS_AWS_PROFILE_NAME]
                   [-s SHOW_USERS_WITH_NO_USAGE_WITHIN]
                   [-d DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN]
                   [-D DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN]
                   [-l LIST_USERS_WITH_NO_USAGE_WITHIN] [-ar AWS_REGION] [-L]
                   [-ucao USE_CREDENTIAL_AS_OBJECT | -uap USE_AWS_PROFILE | -uar USE_AWS_ROLE]

DESCRIPTION:
        A small Python tool for managing IAM user accounts on Amazon Web Services (AWS)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Use to check the version of the tool
  --dry-run             Use to check what actions would be carried out upon execution of passed arguments
  --notify-slack        Use to send notification(s) back to slack channel using webhook (Soon to be deprecated)
  -suu SUPER_USERS_URL, --super-users-url SUPER_USERS_URL
                        Use to specify the URL for remote JSON file containing super users in specified awsklean format. 
                        NOTE: This will delete an local copy before attempting to download!
  -japn JENKINS_AWS_PROFILE_NAME, --jenkins-aws-profile-name JENKINS_AWS_PROFILE_NAME
                        Use to specify the profile name to use as default when on Jenkins
  -s SHOW_USERS_WITH_NO_USAGE_WITHIN, -suwnuw SHOW_USERS_WITH_NO_USAGE_WITHIN, --show-users-with-no-usage-within SHOW_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to show a mini report of ALL IAM users in the AWS account outlining any access method for each user that has NOT had any usage within the specified number of days with True, or False otherwise.
  -d DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, -dafuwnuw DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, --deactivate-access-for-users-with-no-usage-within DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to DEACTIVATE any access method of ALL users in the AWS account that have NOT been used within the specified number of days
  -D DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, -Dafuwnuw DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, --delete-access-for-users-with-no-usage-within DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to DELETE any access method of ALL users in the AWS account that have NOT been used within the specified number of days
  -l LIST_USERS_WITH_NO_USAGE_WITHIN, -luwnuw LIST_USERS_WITH_NO_USAGE_WITHIN, --list-users-with-no-usage-within LIST_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to list ALL users in the AWS account that has NOT used at least one of it's access methods within the specified number of days
  -ar AWS_REGION, --aws-region AWS_REGION
                        Use to specify the region tool should use when creating AWS Clients/ Session
  -L, -lutbk, --list-users-to-be-kleaned
                        Use to get a list of all the users accounts that will be remove if --klean-user argument is passed
  -ucao USE_CREDENTIAL_AS_OBJECT, --use-credential-as-object USE_CREDENTIAL_AS_OBJECT
                        Use this to pass an object with AWS access key credentials
  -uap USE_AWS_PROFILE, --use-aws-profile USE_AWS_PROFILE
                        Use this to tell the tool which of your profiles from your AWS credential file on your local machine to use
  -uar USE_AWS_ROLE, --use-aws-role USE_AWS_ROLE
                        Use this to pass in the AWS account number and role name (as a comma-separated string) to be used

REPOSITORY:
        https://github.com/ooaklee/awsklean-iam-tool
```

### `IAM ACCOUNT WITH ACCESS METHOD(S) NOT USED IN SPECIFIED DAYS`
To get a list of IAM accounts that have at least one access method that has not been used in specified
time

``` bash
    python awsklean.py -l 30
```

**OUTPUT**:
```
The user(s) below meet the requirement(s) for access deletion/ deactivation of at least one of their IAM access methods on the AWS account [<ACCOUNT NUMBER OR ALIAS>]
• user1
• user2
• user3
```

**ADDITIONAL INFORMATION**
To notify slack ensure the environment variable `AWSKLEAN_SLACK_WEBHOOK` is set with a valid slack webhook, and
pass the argument `--notify-slack`. The command should look like:

``` bash
    python awsklean.py -l 30 --notify-slack
```

You will received a slack notification similar to:
```
The following user(s) meet the requirements for access deletion/ deactivation of at least one of their IAM access methods on AWS account (<ACCOUNT NUMBER OR ALIAS>): • user1 • user2 • user3
```

### `MICRO REPORT FOR ALL IAM USERS ON AWS ACCOUNT (SHOWS WHETHER THEY HAVE NOT USED ACCESS METHOD)`
To get a micro-report of all the IAM users on AWS account and whether they have not used they access
method
``` bash
    python awsklean.py -s 30
```

**OUTPUT**:
```
{
    "user1": {
        "password_access": "null",
        "access_key_1_access": false,
        "access_key_2_access": true
    },
    "user2": {
        "password_access": "null",
        "access_key_1_access": true,
        "access_key_2_access": "null"
    },
    "user3": {
        "password_access": "null",
        "access_key_1_access": true,
        "access_key_2_access": "null"
    }
}
```

# MORE INFORMATION ABOUT TOOL ON THE WAY
This tool can do a bit more. I will update this README at a later date. 
Use `python awsklean.py --help` to see all the features. 

`REMEMBER!!!`
If in doubt, when running a command, use `--dry-run` argument to stop any modifying changes occurring.


## CONTRIBUTE
- Report an Issue: https://github.com/ooaklee/awsklean-iam-tool/issues
- Submit a Pull Request: https://github.com/ooaklee/awsklean-iam-tool/pulls


## LICENSE
The project is licensed under the MIT license.