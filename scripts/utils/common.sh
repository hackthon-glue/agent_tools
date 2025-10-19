#!/bin/bash
# Common variables and functions

if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

export AWS_REGION=${AWS_REGION:-us-west-2}
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export PROJECT_NAME="recruitment-agentcore"
export ROLE_NAME="RecruitmentAgentCoreExecutionRole"
