#!/usr/bin/env bash
if [[ $# -ge 3 ]]; then
    export CDK_DEPLOY_ACCOUNT=$1
    export CDK_DEPLOY_REGION=$2
    export CDK_DEPLOY_VPC=$3
    shift; shift; shift
    npx cdk deploy "$@"
    exit $?
else
    echo 1>&2 "Provide account, region and VPC as first three args."
    echo 1>&2 "Additional args are passed through to cdk deploy."
    exit 1
fi