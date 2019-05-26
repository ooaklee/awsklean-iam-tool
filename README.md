# AWSKlean - IAM Tool

## SUMMARY
`AWSKlean` is a Python script created to be used as a simple way to manage IAM users on Amazon Web Services (AWS) accounts.
It gives the user the ability to disable, and remove accounts (W.I.P) if they are unused over a specified time frame. 

## REQUIREMENTS
This script requires the following to have core functionality:
* Python 3.6+ (with modules installed)
* AWS IAM profile with `Full Access` on IAM service and ...(MORE TO BE ADDED) - WIP example will be added to the repo


## `QUICK START`

Set up your AWS credentials (in e.g. ``~/.aws/credentials``):
```
[default]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

Then, set up a default region (in e.g. ``~/.aws/config``):
```
[default]
region=us-east-1
```

Then, install `AWSKlean` requirements, by navigating to root directory of the cloned repo and running:
``` bash
pip install -r requirements.txt
```
I often use a virtual environment, more information about setting up a virtual environment can be found [HERE](https://realpython.com/python-virtual-environments-a-primer/)

Then, run your desired commands!
``` bash
python awsklean.py -l 30
```


## FEATURES
**_Tested with Python version 3.6_**

Features include:
- Allows user to get information about whether access methods (Access Key(s) and Console access) for all users (excluding super users) have not used within a set period
- Allows user to disable access methods for IAM users that have not been used within a specified time
- AWSKlean offers integration with Slack via. sending notifications through the use of slack webhook
- Gives a micro-report for all user on AWS account (excluding super users), outlining which of the access methods the user has NOT used in specified time.


## TERMS
- _access method_ - An `access method` is the way how the user connects to AWS account. This can either be access key(s) or console access
- _super users_ - A group of user accounts which should be ignored at all cost by AWSKlean, found in a file with body [like](/superUsers.json). More information can be found [HERE](#SUPER-USERS-JSON)


## `NOTABLE ENVIRONMENT VARIABLES`
* AWSKLEAN_SLACK_WEBHOOK
* JENKINS_URL
* AWS_DEFAULT_REGION
* AWS_ACCESS_KEY_ID
* AWS_SECRET_ACCESS_KEY


## USAGE

### `GETTING TOOL HELP MESSAGE`
To get information on what arguments the tools can take 
``` bash
python awsklean.py --help
```

_ARGUMENT VARIANT(S)_: `-h`, `--help` 


**OUTPUT**:
```
usage: awsklean.py [-h] [-v] [--dry-run] [--notify-slack]
                   [--super-users-url SUPER_USERS_URL]
                   [--jenkins-aws-profile-name JENKINS_AWS_PROFILE_NAME]
                   [-s SHOW_USERS_WITH_NO_USAGE_WITHIN]
                   [-d DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN]
                   [-D DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN]
                   [-l LIST_USERS_WITH_NO_USAGE_WITHIN]
                   [--aws-region AWS_REGION] [-L]
                   [--use-credential-as-object USE_CREDENTIAL_AS_OBJECT | --use-aws-profile USE_AWS_PROFILE | --use-aws-role USE_AWS_ROLE]

DESCRIPTION:
        A small Python tool for managing IAM user accounts on Amazon Web Services (AWS)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --dry-run             Use to check what actions would be carried out upon execution of passed arguments
  --notify-slack        Use to send notification(s) back to slack channel using webhook (Soon to be deprecated)
  --super-users-url SUPER_USERS_URL, --suu SUPER_USERS_URL
                        Use to specify the URL for remote JSON file containing super users in specified awsklean format. 
                        NOTE: This will delete an local copy before attempting to download!
  --jenkins-aws-profile-name JENKINS_AWS_PROFILE_NAME, --japn JENKINS_AWS_PROFILE_NAME
                        Use to specify the profile name to use as default when on Jenkins
  -s SHOW_USERS_WITH_NO_USAGE_WITHIN, --show-users-with-no-usage-within SHOW_USERS_WITH_NO_USAGE_WITHIN, --suwnuw SHOW_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to show a mini report of ALL IAM users in the AWS account outlining any access method for each user that has NOT had any usage within the specified number of days with True, or False otherwise.
  -d DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, --deactivate-access-for-users-with-no-usage-within DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, --dafuwnuw DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to DEACTIVATE any access method of ALL users in the AWS account that have NOT been used within the specified number of days
  -D DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, --delete-access-for-users-with-no-usage-within DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN, --Dafuwnuw DELETE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to DELETE any access method of ALL users in the AWS account that have NOT been used within the specified number of days [W.I.P]
  -l LIST_USERS_WITH_NO_USAGE_WITHIN, --list-users-with-no-usage-within LIST_USERS_WITH_NO_USAGE_WITHIN, --luwnuw LIST_USERS_WITH_NO_USAGE_WITHIN
                        Use this argument to list ALL users in the AWS account that has NOT used at least one of it's access methods within the specified number of days
  --aws-region AWS_REGION, --ar AWS_REGION
                        Use to specify the region tool should use when creating AWS Clients/ Session
  -L, --list-users-to-be-kleaned, --lutbk
                        Use to get a list of all the users accounts that will be remove if --klean-user argument is passed
  --use-credential-as-object USE_CREDENTIAL_AS_OBJECT, --ucao USE_CREDENTIAL_AS_OBJECT
                        Use this to pass an object with AWS access key credentials
  --use-aws-profile USE_AWS_PROFILE, --uap USE_AWS_PROFILE
                        Use this to tell the tool which of your profiles from your AWS credential file on your local machine to use
  --use-aws-role USE_AWS_ROLE, --uar USE_AWS_ROLE
                        Use this to pass in the AWS account number and role name (as a comma-separated string) to be used

REPOSITORY:
        https://github.com/ooaklee/awsklean-iam-tool
```

### `IAM ACCOUNT WITH ACCESS METHOD(S) NOT USED IN SPECIFIED DAYS`
To get a list of IAM user accounts (excluding [super users](#SUPER-USERS-JSON)) that have at least one access method that has not been used in specified
time

``` bash
python awsklean.py -l 30
```

_ARGUMENT VARIANT(S)_: `-l`, `--luwnuw`, `--list-users-with-no-usage-within`

_ARGUMENT OPTION_: `LIST_USERS_WITH_NO_USAGE_WITHIN` - A number of days (type: `int`) 

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

### `MICRO-REPORT FOR ALL IAM USERS ON AWS ACCOUNT (SHOWS WHETHER THEY HAVE NOT USED ACCESS METHOD)`
To get a micro-report of all the IAM users on AWS account (excluding [super users](#SUPER-USERS-JSON)) and whether they have not used their access
method(s) in passed number of days.
``` bash
python awsklean.py -s 30
```

_ARGUMENT VARIANT(S)_: `-s`, `--suwnuw`, `--show-users-with-no-usage-within`

_ARGUMENT OPTION_: `SHOW_USERS_WITH_NO_USAGE_WITHIN` - A number of days (type: `int`)

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

**ADDITIONAL INFORMATION**

Breaking down the micro-report

`"null"` - This means the access method is not activated on the IAM user account.

`true` - This means the access method has **NOT** been used in the given number of days by the IAM user account.

`false` - This means the access method has been used in the given number of days by the IAM user account.

### `DEACTIVATE ACCESS METHOD(S) NOT USED WITHIN X DAYS`
To deactivate any access methods that have not been used by user(s) (excluding [super users](#SUPER-USERS-JSON)) within passed number of days.
``` bash
python awsklean.py -d 30
```

_ARGUMENT VARIANT(S)_: `-d`, `--dafuwnuw`, `--deactivate-access-for-users-with-no-usage-within`

_ARGUMENT OPTION_: `DEACTIVATE_ACCESS_FOR_USERS_WITH_NO_USAGE_WITHIN` - A number of days (type: `int`)

**OUTPUT**:

```
deactiving access_key_2 XXXXXXXXXXXXXXXX for user (user1) on AWS account <ACCOUNT NUMBER OR ALIAS>
[LIVE MODE] DEACTIVATED KEY XXXXXXXXXXXXXXXX FOR user1 ON AWS ACCOUNT <ACCOUNT NUMBER OR ALIAS>
deactiving access_key_1 AAAAAAAAAAAAAAAAAA for user (user2) on AWS account <ACCOUNT NUMBER OR ALIAS>
[LIVE MODE] DEACTIVATED KEY AAAAAAAAAAAAAAAAAA FOR user2 ON AWS ACCOUNT <ACCOUNT NUMBER OR ALIAS>
deactiving access_key_1 QQQQQQQQQQQQQQQQQQ for user (user3) on AWS account <ACCOUNT NUMBER OR ALIAS>
[LIVE MODE] DEACTIVATED KEY QQQQQQQQQQQQQQQQQQ FOR user3 ON AWS ACCOUNT <ACCOUNT NUMBER OR ALIAS>
```

**ADDITIONAL INFORMATION**
This arguments can be run in a "safe mode" by passing `--dry-run` with arguments. It also makes
use of the `--notify-slack` argument.

The command when using dry run will look similar to:
``` bash
python awsklean.py -d 30 --dry-run
```

Expect to see an output that looks as follows:
```
deactiving access_key_2 XXXXXXXXXXXXXXXX for user (user1) on AWS account <ACCOUNT NUMBER OR ALIAS>
[DRY-RUN MODE] DEACTIVATED KEY XXXXXXXXXXXXXXXX FOR user1 ON AWS ACCOUNT <ACCOUNT NUMBER OR ALIAS>
deactiving access_key_1 AAAAAAAAAAAAAAAAAA for user (user2) on AWS account <ACCOUNT NUMBER OR ALIAS>
[DRY-RUN MODE] DEACTIVATED KEY AAAAAAAAAAAAAAAAAA FOR user2 ON AWS ACCOUNT <ACCOUNT NUMBER OR ALIAS>
deactiving access_key_1 QQQQQQQQQQQQQQQQQQ for user (user3) on AWS account <ACCOUNT NUMBER OR ALIAS>
[DRY-RUN MODE] DEACTIVATED KEY QQQQQQQQQQQQQQQQQQ FOR user3 ON AWS ACCOUNT <ACCOUNT NUMBER OR ALIAS>
```

When using `--notify-slack` the message on slack will be very similar to the message above. It can be passed
in the same command as `--dry-run`, for example:
``` bash
python awsklean.py -d 30 --dry-run --notify-slack
```

### `OVERRIDING AWS CREDENTIALS`
`AWSKlean` uses boto3 an as such will use the default AWS profile on the executing machine unless explicity told to use another account. There are three arguments you can use to override the default behaviour.

#### `USING ANOTHER AWS PROFILE`
If you have multiple profiles in your AWS credential file you can tell `AWSKlean` to use one by passing its name. This will allow `AWSKlean` to run commands on other accounts so long the profile used has the correct permissions to the `IAM service` 

``` bash
python awsklean.py -l 30 --uap exampleprofile
```

_ARGUMENT VARIANT(S)_: `--uap`, `--use-aws-profile`

_ARGUMENT OPTION_: `USE_AWS_PROFILE` - profile name to use (type: `string`)

#### `USING AN AWS ROLE`
Once you've configured your [role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) (it should be able to take calls for your 'master' AWS account number and have permission to IAM service), you can tell `AWSKlean` Use can use the AWS role with

``` bash
python awsklean.py -l 30 --uar "11122223333,awsklean"
```

_ARGUMENT VARIANT(S)_: `--uar`, `--use-aws-role`

_ARGUMENT OPTION_: `USE_AWS_ROLE` - The AWS account number and role name seperated by a comma (type: `string`)

#### `PASSING AWS CREDENTIAL AS AN "OBJECT"`
In the event, you don't have the AWS credential file set-up, and you don't have the AWS environment variables set (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) either OR you just want to pass your desired access key through as an argument. You can pass the credentials you would like AWSKlean use as an "object" (very loosely used)

``` bash
python awsklean.py -l 30 --ucao "{ 'aws_key_id': 'ABCDefGHijkL123', 'aws_secret': 'AWSv3ryS3cr37k3y' }"
```

_ARGUMENT VARIANT(S)_: `--ucao`, `--use-credential-as-object`

_ARGUMENT OPTION_: `USE_CREDENTIAL_AS_OBJECT` - The AWS access key credential you wish to use, it is essential to take note of the application of single and double quotes 

For clarity,
```
"{ 'aws_key_id': '<INSERT_AWS_KEY_HERE>', 'aws_secret': '<INSERT_AWS_SECRET_HERE>' }" 
```

(type: `string`)

#### `PASSING AWS REGION`
If you need to override the AWS region variable

``` bash
python awsklean.py -l 30 --ucao "{ 'aws_key_id': 'ABCDefGHijkL123', 'aws_secret': 'AWSv3ryS3cr37k3y' }" --ar us-east-2
```

_ARGUMENT VARIANT(S)_: `--ar`, `--aws-region`

_ARGUMENT OPTION_: `AWS_REGION` - The AWS region you wish to use (type: `string`)

#### `USING ANOTHER AWS PROFILE (ON JENKINS)`
If you decide to run `AWSKlean` on your Jenkins server as a means of periodically checking the state of your AWS account(s) and you have a specific profile in the server's AWS credential file you wish to use, you can use the `--japn` argument.

``` bash
python awsklean.py -l 30 --japn jenkinsuserprofile --notify-slack
```

_ARGUMENT VARIANT(S)_: `--japn`, `--jenkins-aws-profile-name`

_ARGUMENT OPTION_: `JENKINS_AWS_PROFILE_NAME` - The profile name on your jenkins server to use (type: `string`)


### `SUPER USERS JSON`
In the context of AWSKlean, `super users` are IAM user accounts that you wish for the tool to ignore when creating its reports, or running any modifying changes.

If a `superUsers.json` is located next to the script, it will use that. This means that if you need to add new users, you have to ensure that this file is kept up-to-date locally or remotely. Additionally, you can point `AWSKlean` to a list on a remote server/ website (reachable by the machine running `AWSKlean`) by using the arguments `--suu` OR `--super-users-url`. 

for example:

``` bash
python awsklean.py -l 30 --super-users-url http://s000.tinyupload.com/?file_id=61358988828110367310 --notify-slack
```

_ARGUMENT VARIANT(S)_: `--suu`, `--super-users-url`

_ARGUMENT OPTION_: `SUPER_USERS_URL` - A URL to a [super users file](superUsers.json)

As its only a JSON file, you can use a website such as [Tiny Upload](http://www.tinyupload.com/) to serve your version of this [file](superUsers.json).    

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