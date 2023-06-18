from typing import Optional, Union
from aws_cdk import aws_ec2 as ec2
import aws_cdk as cdk
from constructs import Construct

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
        scope: Construct,
        construct_id: str,
        environment_name: str,
        ui_subdomain: Union[str, None],
        include_rinkeby: bool = False,
        config_service_uri: Optional[str] = None,
        client_gateway_url: Optional[str] = None,
        mainnet_transaction_gateway_url: Optional[str] = None,
        rinkeby_transaction_gateway_url: Optional[str] = None,
        ssl_certificate_arn: Optional[str] = None,
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
            number_of_workers=4,
            ssl_certificate_arn=ssl_certificate_arn,
            **kwargs,
        )
        if include_rinkeby:
            transaction_rinkeby_stack = GnosisSafeTransactionStack(
                self,
                "GnosisTxRinkeby",
                vpc=vpc,
                shared_stack=shared_stack,
                chain_name="rinkeby",
                database=shared_stack.rinkeby_database,
                alb=shared_stack.transaction_rinkeby_alb,
                number_of_workers=1,
                **kwargs,
            )

        client_gateway_stack = GnosisSafeClientGatewayStack(
            self,
            "GnosisCGW",
            vpc=vpc,
            shared_stack=shared_stack,
            ssl_certificate_arn=ssl_certificate_arn,
            config_service_uri=config_service_uri,
            **kwargs,
        )

        configuration_stack = GnosisSafeConfigurationStack(
            self,
            "GnosisCfg",
            vpc=vpc,
            shared_stack=shared_stack,
            ssl_certificate_arn=ssl_certificate_arn,
            client_gateway_url=client_gateway_url,
            mainnet_transaction_gateway_url=mainnet_transaction_gateway_url,
            rinkeby_transaction_gateway_url=rinkeby_transaction_gateway_url,
            **kwargs,
        )

        configuration_stack.node.add_dependency(client_gateway_stack)
        configuration_stack.node.add_dependency(shared_stack)

        transaction_mainnet_stack.node.add_dependency(shared_stack)
        if include_rinkeby:
            transaction_rinkeby_stack.node.add_dependency(shared_stack)
        client_gateway_stack.node.add_dependency(shared_stack)

        GnosisSafeUIStack(
            self,
            "GnosisUI",
            environment_name=environment_name,
            shared_stack=shared_stack,
            subdomain_name=ui_subdomain,
            allowed_origins=[
                "https://safe-client.mainnet.gnosis.yearn.tools",
                "https://safe-transaction.mainnet.gnosis.yearn.tools"
            ],
            **kwargs,
        )
