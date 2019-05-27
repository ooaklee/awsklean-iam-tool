#!/bin/env bash


script_dir="$( cd "$( dirname "$0" )" && pwd )"
script_name="$0"
PYTHON_VERSION=python3.6
LOCAL_REPO="${script_dir}/awsklean-iam-tool"

function helper()
{
    cat <<HELPER
$0 - Shell script wrapper for awsklean

USAGE:
bash $0 --passthrough <AWSKLEAN COMMANDS([ARGUMENT,OPTION]:)> --aws-account-numbers <AWS ACCOUNT NUMBERS>
        --aws-profile <NAME OF ROLE ON AWS ACCOUNTS>
        --help

        --help          Shows this output
        --passthrough   Use this command to passthrough arguments to awsklean tool. Please make sure python arguments and corresponding
                        options are separated using a comma, and different arguments are separated using a :
        <AWSKLEAN COMMANDS([ARGUMENT,OPTION]:)>
                        An example of the argument is -
                         bash $0 --passthrough  "-l,30:--notify-slack"
        --aws-profile   Use this command to declare the name of the AWS IAM role awsklean should connect using
        <NAME OF ROLE ON AWS ACCOUNTS>
                        An example of the argument is -
                         bash $0 --passthrough  "-l,30:--notify-slack" --aws-profile "awsklean_role" --aws-account-numbers "111111111,22222222,33333333"
        --aws-account-numbers   Use this command to pass through AWS account numbers you would like to run the passthrough commands against.
                        NOTE - you will have to pass through --aws-profile otherwise this command will error.
        <AWS ACCOUNT NUMBERS>
                        Comma seperated string of account numbers
                        An example of the argument is -
                         bash $0 --passthrough  "-l,30:--notify-slack" --aws-account-numbers "111111111,22222222,33333333"
HELPER
}

# output message
function output_message()
{
    echo -e ">>> $1\n"
}


# Check if repo exist and up-to-date or pull otherwise
function check_and_pull_latest_from_repo()
{
    if [  ! -d "${LOCAL_REPO}" ]; then
        # Create a directory
        output_message "Creating directory (${LOCAL_REPO})"
        mkdir -p "${LOCAL_REPO}"
    fi

    # Download files to desired directory
    output_message "Downloading latest version(s) of awsklean and requiements"
    curl -L -o "${LOCAL_REPO}/awsklean.py" https://raw.github.com/ooaklee/awsklean-iam-tool/master/awsklean.py && curl -L -o "${LOCAL_REPO}/requirements.txt" https://raw.github.com/ooaklee/awsklean-iam-tool/master/requirements.txt  
}

# Make sure argument passed is authentic
function check_option_argument()
{
    if [[ "$1" =~ ^--.*|^SLACK.* || "$1" == "" ]]; then
        output_message "This is not a valid argument for this option"
        helper
        exit 1
    fi
}

# Check for help long argument
function check_for_helper_long_argument()
{
    # Check for --help option anywhere and show man and exit (takes precendence over all other long options)
    for argument in $*
    do
        if [[ $argument == "--help" ]]; then
            helper
            exit
        fi
    done

}

#•# IN THE BEGINNING...

# Make sure at least one argument is passed
if [ "$#" -lt 1 ]; then
    output_message "Illegal number of parameters"
    helper
    exit 1
fi

# Check if --help is passed 
check_for_helper_long_argument $*

# Delete virtual env dir if exists
if [ -d "${script_dir}/venv" ]; then
    output_message "Deleting previous virtual venv"
    rm -rf "${script_dir}/venv"
fi

# Create venv dir
output_message "Creating virtual venv"
virtualenv -p ${PYTHON_VERSION} "${script_dir}/venv"

# Check for error and exit
if [ "$?" -ne 0 ]; then
    output_message "ERROR: Couldn't find ${PYTHON_VERSION} on host machine. Script will now exit"
    exit 1
fi

# Source venv
output_message "Source virtual venv"	
source "${script_dir}/venv/bin/activate"

# Pull awsklean repo
check_and_pull_latest_from_repo

# Install requirements
output_message "Installing requirements for virtual venv"
pip install -r "${LOCAL_REPO}/requirements.txt"


function run_awsklean_python()
{
    # Get arguments and options
    argument_string=$1

    # Turn all seperators to commas
    comma_string=$( echo $argument_string | sed 's/:/,/g')

    # Use python to create argument as manually passing into awsklean
    arguments_insert_ready=$(${PYTHON_VERSION}<<CONV
# -*- coding: utf-8 -*-

def return_as_double_quote_surrounded(string):
    hold_arr = string.split(',')
    print(" ".join('{0}'.format(arg) for arg in hold_arr))

return_as_double_quote_surrounded("$comma_string")
CONV
)

    # Run awsklean
    if [ -z "$AWSKLEAN_WRAPPER_ACCOUNT_NUMBERS" ]; then
       ${PYTHON_VERSION} "${LOCAL_REPO}/awsklean.py" $arguments_insert_ready
    else
        # Split account number string to array
        IFS=',' read -r -a account_number_array <<< "$AWSKLEAN_WRAPPER_ACCOUNT_NUMBERS"

        # Loop through passed accounts
        for aws_account_number in "${account_number_array[@]}"; do
            # Check if role declared
            if [ -z "$AWSKLEAN_WRAPPER_ROLE_NAME" ]; then
                echo -e "\nERROR:\nTo use --aws-account-numbers OR to have the environment variable \$AWSKLEAN_WRAPPER_ACCOUNT_NUMBERS set \nyou must pass a corresponding AWS IAM role name using --aws-profile"
                exit 1
            else
                # Loop through accounts
                ${PYTHON_VERSION} "${LOCAL_REPO}/awsklean.py" $arguments_insert_ready --use-aws-role "${aws_account_number},${AWSKLEAN_WRAPPER_ROLE_NAME}"
                sleep 5
            fi
        done
    fi
}


# Check if long argument has been passed
output_place_counter=0
for argument in $*
do
    output_place_counter=$(( output_place_counter + 1))

    if [[ $argument == "--aws-account-numbers" ]]; then
        i=$(( output_place_counter + 1))

        # W.I.P
        option_argument=$(echo $* | cut -d' ' -f${i} )

        #Check argument is valid
        check_option_argument "${option_argument}"

        export AWSKLEAN_WRAPPER_ACCOUNT_NUMBERS="${option_argument}"
    fi

    if [[ $argument == "--aws-profile" ]]; then
        i=$(( output_place_counter + 1))
        option_argument=$(echo $* | cut -d' ' -f${i} )

        #Check argument is valid
        check_option_argument ${option_argument}

        export AWSKLEAN_WRAPPER_ROLE_NAME="${option_argument}"
    fi

    if [[ $argument == "--passthrough" ]]; then
        i=$(( output_place_counter + 1))
        option_argument=$(echo $* | cut -d' ' -f${i} )

        # Check argument is valid
        check_option_argument "${option_argument}"

        # Call function
        run_awsklean_python "${option_argument}"
    fi
done
