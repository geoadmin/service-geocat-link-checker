# geocat.ch link checker
This version is aimed at being hosted and run into an AWS lambda function. It uses the AWS python SDK boto3 to access SES and send emails.
Since everything runs inside AWS, no AWS credentials is required.

## Build Lambda Deployment Package
Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```
Install dependencies
```bash
pip install -r requirements.txt
```
Deactivate the virtual environment and build a deployment package for lambda as zip file 
```bash
deactivate
cd .venv/lib/python3.x/site-packages
zip -r ../../../../deployment_package.zip .
cd ../../../../
zip deployment_package.zip main.py link_checker.py settings.py utils.py
```
## Deploy package on AWS Lambda
* Create an IAM role with `AmazonSESFullAccess` and `CloudWatchFullAccess` permissions
* Create a new lambda function with runtime python3.x and change default execution role to use the role created above
* Upload deployment package (.zip file)
* Set up runtime handler info to `main.lambda_handler`
* Set up max running time and max memory accordingly




