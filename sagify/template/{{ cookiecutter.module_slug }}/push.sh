#!/usr/bin/env bash

image={{ cookiecutter.project_slug }}-img
tag=$1
region=$2
role=$3
profile=$4
external_id=$5

if [[ ! -z "$role" ]]; then 
    aws configure set profile.${role}.role_arn ${role}
    if [[ ! -z "$external_id" ]]; then 
        aws configure set profile.${role}.external_id ${external_id}
    fi
    aws configure set profile.${role}.source_profile default
    profile=${role}
elif [ -z "$profile" ]; then 
    profile={{ cookiecutter.aws_profile }}
fi 

if [ -z "$region" ]; then 
    region={{ cookiecutter.aws_region }}
fi 

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --profile ${profile} --query Account --output text)
if [ $? -ne 0 ]; then
    exit 255
fi

# If the repository doesn't exist in ECR, create it.
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:${tag}"
aws ecr describe-repositories --profile ${profile} --region ${region} --repository-names "${image}" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "Creating ECR repository"
    aws ecr create-repository --profile ${profile} --region ${region} --repository-name "${image}" > /dev/null
else 
    echo "ECR repository already exists, will push there."
fi

# Get the login command from ECR and execute it directly
$(aws ecr get-login --profile ${profile} --region ${region} --no-include-email)

# Push Docker image to ECR
docker tag ${image}:${tag} ${fullname}
docker push ${fullname}
