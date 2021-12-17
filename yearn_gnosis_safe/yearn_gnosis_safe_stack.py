from aws_cdk import aws_ec2 as ec2
from aws_cdk import core as cdk

from yearn_gnosis_safe.gnosis_safe_client_gateway_stack import \
    GnosisSafeClientGatewayStack
from yearn_gnosis_safe.gnosis_safe_configuration_stack import \
    GnosisSafeConfigurationStack
from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack
from yearn_gnosis_safe.gnosis_safe_transaction_stack import \
    GnosisSafeTransactionStack
from yearn_gnosis_safe.gnosis_safe_ui_stack import GnosisSafeUIStack


class YearnGnosisSafeStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        environment_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            "GnosisVPC",
            max_azs=2,
        )

        shared_stack = GnosisSafeSharedStack(self, "GnosisShared", vpc=vpc, **kwargs)

        transaction_mainnet_stack = GnosisSafeTransactionStack(
            self,
            "GnosisTxMainnet",
            vpc=vpc,
            shared_stack=shared_stack,
            chain_name="mainnet",
            database=shared_stack.mainnet_database,
            alb=shared_stack.transaction_mainnet_alb,
            number_of_workers=8,
            **kwargs,
        )

        transaction_rinkeby_stack = GnosisSafeTransactionStack(
            self,
            "GnosisTxRinkeby",
            vpc=vpc,
            shared_stack=shared_stack,
            chain_name="rinkeby",
            database=shared_stack.rinkeby_database,
            alb=shared_stack.transaction_rinkeby_alb,
            number_of_workers=2,
            **kwargs,
        )

        client_gateway_stack = GnosisSafeClientGatewayStack(
            self,
            "GnosisCGW",
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

        configuration_stack.node.add_dependency(client_gateway_stack)
        configuration_stack.node.add_dependency(shared_stack)

        transaction_mainnet_stack.node.add_dependency(shared_stack)
        transaction_rinkeby_stack.node.add_dependency(shared_stack)
        client_gateway_stack.node.add_dependency(shared_stack)

        GnosisSafeUIStack(
            self,
            "GnosisUI",
            environment_name=environment_name,
            shared_stack=shared_stack,
            **kwargs,
        )
