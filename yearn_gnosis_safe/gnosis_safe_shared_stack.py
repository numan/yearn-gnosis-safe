import json

from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_rds as rds
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import core as cdk


class GnosisSafeSharedStack(cdk.Stack):
    @property
    def database(self):
        return self._database

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
    def transaction_alb(self):
        return self._transaction_alb

    @property
    def client_gateway_alb(self):
        return self._client_gateway_alb

    def __init__(
        self,
        scope: cdk.Construct,
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
                        "TX_DJANGO_SECRET_KEY": "",
                        "TX_DATABASE_URL": "",
                        "TX_ETHEREUM_NODE_URL": "",
                        "TX_ETHEREUM_TRACING_NODE_URL": "",
                        "CFG_SECRET_KEY": "",
                        "CFG_DJANGO_SUPERUSER_USERNAME": "",
                        "CFG_DJANGO_SUPERUSER_PASSWORD": "",
                        "CFG_DJANGO_SUPERUSER_EMAIL": "",
                        "CGW_ROCKET_SECRET_KEY": "",
                        "CGW_WEBHOOK_TOKEN": "",
                        "CGW_EXCHANGE_API_KEY": "",
                    }
                ),
                generate_string_key="password",  # Needed just to we can provision secrets manager with a template. Not used.
            ),
        )

        self._config_alb = elbv2.ApplicationLoadBalancer(
            self, "CfgGnosis", vpc=vpc, internet_facing=True
        )

        self._transaction_alb = elbv2.ApplicationLoadBalancer(
            self, "TxGnosis", vpc=vpc, internet_facing=True
        )

        self._client_gateway_alb = elbv2.ApplicationLoadBalancer(
            self, "ClientGatewayGnosis", vpc=vpc, internet_facing=True
        )

        self._log_group = logs.LogGroup(
            self, "LogGroup", retention=logs.RetentionDays.ONE_MONTH
        )

        self._database = rds.DatabaseInstance(
            self,
            "PostgresDB",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13_4
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.SMALL
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            max_allocated_storage=500,
            credentials=rds.Credentials.from_generated_secret("postgres"),
        )

