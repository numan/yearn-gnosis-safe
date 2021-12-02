from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk
from yearn_gnosis_safe.gnosis_safe_client_gateway_stack import (
    GnosisSafeClientGatewayStack,
)
from yearn_gnosis_safe.gnosis_safe_configuration_stack import (
    GnosisSafeConfigurationStack,
)

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack
from yearn_gnosis_safe.gnosis_safe_transaction_stack import GnosisSafeTransactionStack


class YearnGnosisSafeStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "GnosisVPC",
            max_azs=2,
        )

        shared_stack = GnosisSafeSharedStack(self, "GnosisShared", vpc=vpc, **kwargs)

        transaction_stack = GnosisSafeTransactionStack(
            self,
            "GnosisTx",
            vpc=vpc,
            shared_stack=shared_stack,
            **kwargs,
        )

        configuration_stack = GnosisSafeConfigurationStack(
            self,
            "GnosisCfg",
            vpc=vpc,
            shared_stack=shared_stack,
            **kwargs,
        )

        client_gateway_stack = GnosisSafeClientGatewayStack(
            self,
            "GnosisCGW",
            vpc=vpc,
            shared_stack=shared_stack,
            **kwargs,
        )
