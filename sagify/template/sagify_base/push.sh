#!/usr/bin/env bash

tag=$1
region=$2
role=$3
profile=$4
external_id=$5
image=$6
aws_version=`aws --version`

if [[ ! -z "$role" ]]; then 
    aws configure set profile.${role}.role_arn ${role}
    if [[ ! -z "$external_id" ]]; then
        aws configure set profile.${role}.external_id ${external_id}
    fi

    if [[ -z "$profile" ]]; then
        aws configure set profile.${role}.credential_source Ec2InstanceMetadata
    else
        aws configure set profile.${role}.source_profile ${profile}
    fi
    profile=${role}
fi

# Get the account number associated with the current IAM credentials

if [[ ! -z "$profile" ]]; then
    account=$(aws sts get-caller-identity --profile ${profile} --query Account --output text)
else
    account=$(aws sts get-caller-identity --query Account --output text)
fi

if [ $? -ne 0 ]; then
    exit 255
fi

# If the repository doesn't exist in ECR, create it.
fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:${tag}"

if [[ ! -z "$profile" ]]; then
    aws ecr describe-repositories --profile ${profile} --region ${region} --repository-names "${image}" > /dev/null 2>&1
else
    aws ecr describe-repositories --region ${region} --repository-names "${image}" > /dev/null 2>&1
fi

if [ $? -ne 0 ]; then
    echo "Creating ECR repository"
    if [[ ! -z "$profile" ]]; then
        aws ecr create-repository --profile ${profile} --region ${region} --repository-name "${image}" > /dev/null
    else
        aws ecr create-repository --region ${region} --repository-name "${image}" > /dev/null
    fi
else
    echo "ECR repository already exists, will push there."
fi

if [[ $aws_version == aws-cli/2* ]]; then
# Get the login command from ECR and execute it directly
    if [[ ! -z "$profile" ]]; then
        aws ecr get-login-password --profile ${profile} --region ${region} | docker login --username AWS --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com
    else
        aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin "${account}".dkr.ecr."${region}".amazonaws.com
    fi
else
    if [[ ! -z "$profile" ]]; then
        $(aws ecr get-login --profile ${profile} --region ${region} --no-include-email)
    else
        $(aws ecr get-login --region ${region} --no-include-email)
    fi
fi

# Push Docker image to ECR
docker tag ${image}:${tag} ${fullname}
docker push ${fullname}
