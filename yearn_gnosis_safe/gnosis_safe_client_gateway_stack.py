from typing import Optional
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import core as cdk
from aws_cdk import aws_elasticloadbalancingv2 as elbv2

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack
from yearn_gnosis_safe.redis_stack import RedisStack


class GnosisSafeClientGatewayStack(cdk.Stack):
    @property
    def redis_cluster(self):
        return self._redis_cluster

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        shared_stack: GnosisSafeSharedStack,
        cache_node_type: str = "cache.t3.small",
        ssl_certificate_arn: Optional[str] = None,
        config_service_uri: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if config_service_uri is None:
            config_service_uri = f"http://{shared_stack.config_alb.load_balancer_dns_name}"

        self._redis_cluster = RedisStack(
            self, "RedisCluster", vpc=vpc, cache_node_type=cache_node_type
        )

        ecs_cluster = ecs.Cluster(
            self,
            "GnosisSafeCluster",
            enable_fargate_capacity_providers=True,
            vpc=vpc,
        )

        container_args = {
            "image": ecs.ContainerImage.from_asset("docker/client-gateway"),
            "environment": {
                "CONFIG_SERVICE_URI": config_service_uri,
                "FEATURE_FLAG_NESTED_DECODING": "true",
                "SCHEME": "http",
                "ROCKET_LOG_LEVEL": "normal",
                "ROCKET_PORT": "3666",
                "ROCKET_ADDRESS": "0.0.0.0",
                "RUST_LOG": "debug",
                "LOG_ALL_ERROR_RESPONSES": "true",
                "INTERNAL_CLIENT_CONNECT_TIMEOUT": "10000",
                "SAFE_APP_INFO_REQUEST_TIMEOUT": "10000",
                "CHAIN_INFO_REQUEST_TIMEOUT": "15000",
                "REDIS_URI": self.redis_connection_string,
                "EXCHANGE_API_BASE_URI": "http://api.exchangeratesapi.io/latest",
                "VPC_TRANSACTION_SERVICE_URI": "false",
                "TX_QUEUED_CACHE_DURATION": "1000",
                "REQUEST_CACHE_DURATION": "10000",
            },
            "secrets": {
                "ROCKET_SECRET_KEY": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CGW_ROCKET_SECRET_KEY"
                ),
                "WEBHOOK_TOKEN": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CGW_WEBHOOK_TOKEN"
                ),
                "EXCHANGE_API_KEY": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CGW_EXCHANGE_API_KEY"
                ),
            },
        }

        ## Web
        web_task_definition = ecs.FargateTaskDefinition(
            self,
            "SafeCGWServiceWeb",
            cpu=512,
            memory_limit_mib=1024,
            family="GnosisSafeServices",
        )

        web_task_definition.add_container(
            "Web",
            container_name="web",
            working_directory="/app",
            logging=ecs.AwsLogDriver(
                log_group=shared_stack.log_group,
                stream_prefix="Web",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            port_mappings=[ecs.PortMapping(container_port=3666)],
            **container_args,
        )

        service = ecs.FargateService(
            self,
            "WebService",
            cluster=ecs_cluster,
            task_definition=web_task_definition,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            enable_execute_command=True,
            desired_count=1,
        )

        ## Setup LB and redirect traffic to web and static containers

        listener = shared_stack.client_gateway_alb.add_listener("Listener", port=80)

        listener.add_targets(
            "WebTarget",
            port=80,
            targets=[service.load_balancer_target(container_name="web")],
            health_check=elbv2.HealthCheck(path="/health"),
        )

        if ssl_certificate_arn is not None:

            ssl_listener = shared_stack.client_gateway_alb.add_listener(
                "SSLListener", port=443
            )

            ssl_listener.add_certificate_arns(
                "SSL Listener",
                arns=[ssl_certificate_arn],
            )

            ssl_listener.add_targets(
                "WebTarget",
                protocol=elbv2.ApplicationProtocol.HTTP,
                targets=[service.load_balancer_target(container_name="web")],
                health_check=elbv2.HealthCheck(path="/health"),
            )

        for service in [service]:
            service.connections.allow_to(
                self.redis_cluster.connections, ec2.Port.tcp(6379), "Redis"
            )

    @property
    def redis_connection_string(self) -> str:
        return f"redis://{self.redis_cluster.cluster.attr_primary_end_point_address}:{self.redis_cluster.cluster.attr_primary_end_point_port}"
