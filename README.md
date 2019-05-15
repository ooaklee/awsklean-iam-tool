# AWSKlean - IAM Tool

## SUMMARY
`AWSKlean` is a Python script created to be used as a simple way to manage IAM profiles on AWS accounts.
It gives the user the ability to disable,  and remove accounts if they are unused over a specified time frame
and as such deemed to be a "problem" account. 

## REQUIREMENTS
This script requires the following to have core functionality:
* Python 3.6+ (with modules installed)
* AWS IAM profile with `Full Access` on IAM service

**ADDITIONAL NICE TO HAVES**
* AWS Roles with STS configured to take requests from main AWS accounts (If you would like to manage multiple accounts)


