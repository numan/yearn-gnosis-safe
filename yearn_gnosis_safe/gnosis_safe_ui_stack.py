from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_s3_deployment as s3_deployment
from aws_cdk.aws_cloudfront import AllowedMethods

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack


class GnosisSafeUIStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        environment_name: str,
        shared_stack: GnosisSafeSharedStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            f"{environment_name.upper()}Bucket",
            website_index_document="index.html",
            public_read_access=True,
            auto_delete_objects=True,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.POST],
                    allowed_headers=["*"],
                    allowed_origins=[
                        f"http://{shared_stack.client_gateway_alb.load_balancer_dns_name}",
                        f"http://{shared_stack.transaction_alb.load_balancer_dns_name}",
                    ],
                )
            ],
        )

        s3_deployment.BucketDeployment(
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
