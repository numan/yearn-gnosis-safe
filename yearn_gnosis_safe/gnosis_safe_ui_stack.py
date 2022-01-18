from typing import Optional, Sequence
from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack


class GnosisSafeUIStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        environment_name: str,
        shared_stack: GnosisSafeSharedStack,
        subdomain_name = None,
        allowed_origins: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        if allowed_origins is None:
            allowed_origins = []

        bucket = s3.Bucket(
            self,
            f"{environment_name.upper()}Bucket",
            website_index_document="index.html",
            public_read_access=True,
            auto_delete_objects=True,
            bucket_name=subdomain_name,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.POST],
                    allowed_headers=["*"],
                    allowed_origins=[
                        f"http://{shared_stack.client_gateway_alb.load_balancer_dns_name}",
                        f"http://{shared_stack.transaction_mainnet_alb.load_balancer_dns_name}",
                        f"http://{shared_stack.transaction_rinkeby_alb.load_balancer_dns_name}",
                    ] + allowed_origins,
                )
            ],
            website_routing_rules=[
                s3.RoutingRule(
                    condition=s3.RoutingRuleCondition(http_error_code_returned_equals="404"),
                    replace_key=s3.ReplaceKey.with_("index.html"),
                )
            ],
        )

        bucket_deployment = s3_deployment.BucketDeployment(
            self,
            f"{environment_name.upper()}BucketDeployment",
            sources=[
                s3_deployment.Source.asset(
                    f"docker/ui/builds/build_{environment_name.lower()}"
                )
            ],
            destination_bucket=bucket,
            retain_on_delete=False,
        )
