# AWSKlean - IAM Tool

## SUMMARY
`AWSKlean` is a Python script created to be used as a simple way to manage IAM users on AWS accounts.
It gives the user the ability to disable,  and remove accounts if they are unused over a specified time frame. 

## REQUIREMENTS
This script requires the following to have core functionality:
* Python 3.6+ (with modules installed)
* AWS IAM profile with `Full Access` on IAM service - WIP example will be added to the repo

**ADDITIONAL NICE TO HAVES**
* AWS Roles with STS configured to take requests from main AWS accounts (If you would like to manage multiple accounts)



`NOTE`
* I originally wrote this script a couple years back, and so some operations may have changed. I will try and get basic functionality working as soon as possible