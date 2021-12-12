#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2

from yearn_gnosis_safe.erigon_stack import ErigonEthereumStack

app = cdk.App()


class AppStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc_id = os.environ.get("CDK_DEPLOY_VPC")

        # The code that defines your stack goes here
        ErigonEthereumStack(
            self,
            "ErigonStack",
            vpc=ec2.Vpc.from_lookup(self, "VPC", vpc_id=vpc_id),
            **kwargs
        )


environment = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)
app_stack = AppStack(app, "ErigonApp", env=environment)
cdk.Tags.of(app_stack).add("app", "Erigon Node")


app.synth()
