# Using awsklean in Jenkins pipeline (Example)

## SUMMARY
This folder is an example of how you can use awsklean in a Jenkins pipeline to manage
multiple AWS accounts

## REQUIREMENTS
For this pipeline to work the following conditions must be met.
`JENKINS SYSTEM`
Software:
    • Python 3.6
    • Virtualenv
    • GIT
Credentials:
    More information about credential binding can be found [HERE](https://jenkins.io/doc/pipeline/steps/credentials-binding/)
    • awsklean-default-iam-credentials (**kind**: `Username with password` - usernameVariable is 'AWS_ACCESS_KEY_ID', passwordVariable is 'AWS_SECRET_ACCESS_KEY')
    • awsklean-slack-webhook (**kind**: `Secret Text`)

    NOTE:
    To create a new credential on Jenkins (ver. 2.178): Navigate to 'Credentials' (/credentials) > 'System' (/credentials/store/system/) > Select Domain ( I will use 'Global' (/credentials/store/system/domain/_/)) > 'Add Credentials' > Select **KIND**, update fields, add description > Click 'Save'

`AWS ACCOUNTS`
Main Account:
    • ACCESS KEY which will be used for `awsklean-default-iam-credentials` or set in Jenkin's AWS credential file in `[default]` profile. The Access Key must have permission to modify IAM service, use STS

Sibling Accounts:
    • IAM ROLE `awsklean` with permissions to modify IAM service. See the policy example [HERE](/awsklean-sibling-role-policy-example.json)
    • IAM ROLE must accept commands from `Main Account` (When creating role `type of trusted entity` should be `Another AWS account`)

# How To use
1. Create and clone new repository, then copy contents of this folder (`JENKINS_PIPELINE_EXAMPLE`). Make sure `Jenkinsfile` is in the repo root directory.
2. Update the Jenkins file environment variables to match your desired account numbers, day range and IAM role name of `Sibling Accounts`
3. Update commands passed to `awsklean` by changing option passed using `--passthrough` tag in the Jenkinsfile. 
    NOTE: I advise using shorthand `awsklean` argument codes i.e. `-l`, `-d` where applicable to avoid an eyesore. Split arguments with `:` as advised in wrapper. get more wrapper information by running `bash awsklean_wrapper.sh --help`
4. Push your changes to your repo
5. Make sure `REQUIREMENTS` are met
6. Create a  job in Jenkins for your repo from `step 1` and configure 
7. Run test!