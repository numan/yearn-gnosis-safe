import json

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
import aws_cdk as cdk
from constructs import Construct


class GnosisSafeSharedStack(cdk.Stack):
    @property
    def mainnet_database(self):
        return self._mainnet_database

    @property
    def rinkeby_database(self):
        return self._rinkeby_database

    @property
    def log_group(self):
        return self._log_group

    @property
    def secrets(self):
        return self._secrets

    @property
    def config_alb(self):
        return self._config_alb

    @property
    def transaction_mainnet_alb(self):
        return self._transaction_mainnet_alb

    @property
    def transaction_rinkeby_alb(self):
        return self._transaction_rinkeby_alb

    @property
    def client_gateway_alb(self):
        return self._client_gateway_alb

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._secrets = secretsmanager.Secret(
            self,
            "GnosisSharedSecrets",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps(
                    {
                        # Mainnet
                        "TX_DJANGO_SECRET_KEY_MAINNET": "",
                        "TX_DATABASE_URL_MAINNET": "",
                        "TX_ETHEREUM_NODE_URL_MAINNET": "",
                        "TX_ETHEREUM_TRACING_NODE_URL_MAINNET": "",
                        "TX_ETHERSCAN_API_KEY_MAINNET": "",
                        # Rinkeby
                        "TX_DJANGO_SECRET_KEY_RINKEBY": "",
                        "TX_DATABASE_URL_RINKEBY": "",
                        "TX_ETHEREUM_NODE_URL_RINKEBY": "",
                        "TX_ETHEREUM_TRACING_NODE_URL_RINKEBY": "",
                        "TX_ETHERSCAN_API_KEY_RINKEBY": "",
                        # Configuration Service
                        "CFG_SECRET_KEY": "",
                        "CFG_DJANGO_SUPERUSER_USERNAME": "",
                        "CFG_DJANGO_SUPERUSER_PASSWORD": "",
                        "CFG_DJANGO_SUPERUSER_EMAIL": "",
                        # Client Gateway
                        "CGW_ROCKET_SECRET_KEY": "",
                        "CGW_WEBHOOK_TOKEN": "",
                        "CGW_EXCHANGE_API_KEY": "",
                        # UI
                        "UI_REACT_APP_INFURA_TOKEN": "",
                        "UI_REACT_APP_ETHERSCAN_API_KEY": "",
                        "UI_REACT_APP_ETHGASSTATION_API_KEY": "",
                        "UI_REACT_APP_SAFE_APPS_RPC_INFURA_TOKEN": "",
                    }
                ),
                generate_string_key="password",  # Needed just to we can provision secrets manager with a template. Not used.
            ),
        )

        self._config_alb = elbv2.ApplicationLoadBalancer(
            self, "CfgGnosis", vpc=vpc, internet_facing=True
        )
        cdk.Tags.of(self._config_alb).add("Name", "Gnosis Config")

        self._transaction_mainnet_alb = elbv2.ApplicationLoadBalancer(
            self, "TxGnosisMainnet", vpc=vpc, internet_facing=True
        )
        cdk.Tags.of(self._transaction_mainnet_alb).add(
            "Name", "Gnosis Transaction Mainnet"
        )

        self._transaction_rinkeby_alb = elbv2.ApplicationLoadBalancer(
            self, "TxGnosisRinkeby", vpc=vpc, internet_facing=True
        )
        cdk.Tags.of(self._transaction_rinkeby_alb).add(
            "Name", "Gnosis Transaction Rinkeby"
        )

        self._client_gateway_alb = elbv2.ApplicationLoadBalancer(
            self, "ClientGatewayGnosis", vpc=vpc, internet_facing=True
        )
        cdk.Tags.of(self._client_gateway_alb).add("Name", "Gnosis Client Gateway")

        self._log_group = logs.LogGroup(
            self, "LogGroup", retention=logs.RetentionDays.ONE_MONTH
        )

        # The databases for the transaction service need to be defined here because we need the database credentials
        # as a database URL. This can't be done dynamically because of limitations of CDK/Cloud Formation.

        database_options = {
            "engine": rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13_4
            ),
            "instance_type": ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.SMALL
            ),
            "vpc": vpc,
            "vpc_subnets": ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            "max_allocated_storage": 500,
            "credentials": rds.Credentials.from_generated_secret("postgres"),
        }

        self._mainnet_database = rds.DatabaseInstance(
            self,
            "MainnetTxDatabase",
            **database_options,
        )

        self._rinkeby_database = rds.DatabaseInstance(
            self,
            "RinkebyTxDatabase",
            **database_options,
        )
