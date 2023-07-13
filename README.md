# geocat.ch link checker
Version to be running on a AWS ECS cluster using Fargate. Known as a Fat Lambda strategy. To be able to run a python application in a serverless environment for more than 15 mins (i.e. limitation from AWS Lambda)

## Dockerize the application
Since ECS pulls a Docker image from ECR and then runs it as a container, we first need a Docker image.

Having Docker running on your machine, run the following at the root directory, where the `dockerfile` is :
```bash
docker build -t {docker-image-name} .
```
If you change the code base, you need to rebuild the docker image.

## Push Docker image to AWS ECR
* Login to AWS console and go to ECR service
* Create a new private repository and give it a name
* Go into the newly created repository and click on `view push commands`
* Follow the instruction to push the Docker image from your computer to ECR 
  > (this is using the aws CLI with IAM credentials with enough access to create ECR, ECS, etc. e.g. with policy PowerUserAccess)

If the docker image already exists in ECR, you must change the tag e.g. `latest`

## Create a Fargate cluster in ECS
* Go to AWS ECS service and create a new cluster
* Give it a name. By default it creates a Fargste cluster.
* Leave the VPC and subnets unchanged

## Configure a task definition
* In the ECS service, go to task definitions and create a new task definition
* Give it a name
* Under container details, make sure to give the image URI from the pushed docker image in ECR
* In the environment section, make sure to select the same OS/Architecture as your base docker image (e.g. linuxX86 or arm64, windows)
* Set up the desired cpu and memory capacity
* If your application needs to call other AWS services (send emails through SES, write files into S3), you need to give the task the appopriate role under `Tasks role` > `task role`.
* The `Task execution role` is set by default

## Run the task
Once the task definition is done, you can run the task in the newly created Fargate cluster. You just have to choose the cluster.
