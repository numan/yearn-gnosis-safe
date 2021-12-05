#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from yearn_gnosis_safe.yearn_gnosis_safe_stack import YearnGnosisSafeStack

app = cdk.App()
environment = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)

environment_name = "production"
prod_stack = YearnGnosisSafeStack(
    app, "GnosisSafeStack", environment_name=environment_name, env=environment
)
cdk.Tags.of(prod_stack).add("environment", environment_name)

app.synth()
