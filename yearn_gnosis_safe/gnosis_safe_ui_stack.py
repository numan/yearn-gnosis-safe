from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import core as cdk
from yearn_gnosis_safe.gnosis_safe_configuration_stack import (
    GnosisSafeConfigurationStack,
)

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack
from yearn_gnosis_safe.redis_stack import RedisStack


class GnosisSafeUIStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        shared_stack: GnosisSafeSharedStack,
        environment_name: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self._redis_cluster = RedisStack(self, "RedisCluster", vpc=vpc)

        ecs_cluster = ecs.Cluster(
            self,
            "GnosisSafeCluster",
            enable_fargate_capacity_providers=True,
            vpc=vpc,
        )

        ## Web
        web_task_definition = ecs.FargateTaskDefinition(
            self,
            "SafeUIServiceWeb",
            cpu=512,
            memory_limit_mib=1024,
            family="GnosisSafeServices",
        )

        web_task_definition.add_container(
            "Web",
            image=ecs.ContainerImage.from_asset(
                "docker/ui", build_args={"ENVIRONMENT_NAME": environment_name}
            ),
            container_name="web",
            working_directory="/app",
            logging=ecs.AwsLogDriver(
                log_group=shared_stack.log_group,
                stream_prefix="Web",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            port_mappings=[ecs.PortMapping(container_port=80)],
        )

        service = ecs.FargateService(
            self,
            "WebService",
            cluster=ecs_cluster,
            task_definition=web_task_definition,
            desired_count=1,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            assign_public_ip=True,
            enable_execute_command=True,
        )

        ## Setup LB and redirect traffic to web and static containers

        listener = shared_stack.ui_alb.add_listener("Listener", port=80)

        listener.add_targets(
            "WebTarget",
            port=80,
            targets=[service.load_balancer_target(container_name="web")],
        )
