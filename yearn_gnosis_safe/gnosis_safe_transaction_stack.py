from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import core as cdk
from aws_cdk import aws_elasticloadbalancingv2 as elbv2

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack
from yearn_gnosis_safe.redis_stack import RedisStack


class GnosisSafeTransactionStack(cdk.Stack):
    @property
    def redis_cluster(self):
        return self._redis_cluster

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        shared_stack: GnosisSafeSharedStack,
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

        container_args = {
            "image": ecs.ContainerImage.from_asset("docker/transactions"),
            "environment": {
                "PYTHONPATH": "/app/",
                "DJANGO_SETTINGS_MODULE": "config.settings.production",
                "C_FORCE_ROOT": "true",
                "DEBUG": "0",
                "ETH_L2_NETWORK": "0",
                "REDIS_URL": f"{self.redis_connection_string}/0",
                "CELERY_BROKER_URL": f"{self.redis_connection_string}/1",
                "DJANGO_ALLOWED_HOSTS": "*",
            },
            "secrets": {
                "DJANGO_SECRET_KEY": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "TX_DJANGO_SECRET_KEY"
                ),
                "DATABASE_URL": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "TX_DATABASE_URL"
                ),
                "ETHEREUM_NODE_URL": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "TX_ETHEREUM_NODE_URL"
                ),
                "ETHEREUM_TRACING_NODE_URL": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "TX_ETHEREUM_TRACING_NODE_URL"
                ),
            },
        }

        ## Web
        web_task_definition = ecs.FargateTaskDefinition(
            self,
            "SafeTransactionServiceWeb",
            cpu=512,
            memory_limit_mib=1024,
            family="GnosisSafeServices",
            volumes=[
                ecs.Volume(
                    name="nginx_volume",
                )
            ],
        )

        web_container = web_task_definition.add_container(
            "Web",
            container_name="web",
            working_directory="/app",
            command=["/app/run_web.sh"],
            logging=ecs.AwsLogDriver(
                log_group=shared_stack.log_group,
                stream_prefix="Web",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            port_mappings=[ecs.PortMapping(container_port=8888)],
            **container_args,
        )

        web_container.add_mount_points(
            ecs.MountPoint(
                source_volume="nginx_volume",
                container_path="/app/staticfiles",
                read_only=False,
            )
        )

        nginx_container = web_task_definition.add_container(
            "StaticFiles",
            container_name="static",
            image=ecs.ContainerImage.from_registry("nginx:latest"),
            port_mappings=[ecs.PortMapping(container_port=80)],
        )

        nginx_container.add_mount_points(
            ecs.MountPoint(
                source_volume="nginx_volume",
                container_path="/usr/share/nginx/html/static",
                read_only=True,
            )
        )

        web_service = ecs.FargateService(
            self,
            "WebService",
            cluster=ecs_cluster,
            task_definition=web_task_definition,
            desired_count=1,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            assign_public_ip=True,
            enable_execute_command=True,
        )

        ## Worker
        worker_task_definition = ecs.FargateTaskDefinition(
            self,
            "SafeTransactionServiceWorker",
            cpu=512,
            memory_limit_mib=1024,
            family="GnosisSafeServices",
        )

        worker_task_definition.add_container(
            "Worker",
            container_name="worker",
            command=["docker/web/celery/worker/run.sh"],
            logging=ecs.AwsLogDriver(
                log_group=shared_stack.log_group,
                stream_prefix="Worker",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            **container_args,
        )

        worker_service = ecs.FargateService(
            self,
            "WorkerService",
            cluster=ecs_cluster,
            task_definition=worker_task_definition,
            desired_count=1,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
        )

        ## Scheduled Tasks
        schedule_task_definition = ecs.FargateTaskDefinition(
            self,
            "SafeTransactionServiceSchedule",
            cpu=512,
            memory_limit_mib=1024,
            family="GnosisSafeServices",
        )

        schedule_task_definition.add_container(
            "Schedule",
            container_name="schedule",
            command=["docker/web/celery/scheduler/run.sh"],
            logging=ecs.AwsLogDriver(
                log_group=shared_stack.log_group,
                stream_prefix="schedule",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            **container_args,
        )

        schedule_service = ecs.FargateService(
            self,
            "ScheduleService",
            cluster=ecs_cluster,
            task_definition=schedule_task_definition,
            desired_count=1,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
        )

        ## Setup LB and redirect traffic to web and static containers

        listener = shared_stack.transaction_alb.add_listener("Listener", port=80)

        listener.add_targets(
            "Static",
            port=80,
            targets=[web_service.load_balancer_target(container_name="static")],
            priority=1,
            conditions=[elbv2.ListenerCondition.path_patterns(["/static/*"])],
            health_check=elbv2.HealthCheck(path="/static/drf-yasg/style.css"),
        )
        listener.add_targets(
            "WebTarget",
            port=80,
            targets=[web_service.load_balancer_target(container_name="web")],
        )

        for service in [web_service, worker_service, schedule_service]:
            service.connections.allow_to(
                shared_stack.database, ec2.Port.tcp(5432), "RDS"
            )
            service.connections.allow_to(
                self.redis_cluster.connections, ec2.Port.tcp(6379), "Redis"
            )

    @property
    def redis_connection_string(self) -> str:
        return f"redis://{self.redis_cluster.cluster.attr_primary_end_point_address}:{self.redis_cluster.cluster.attr_primary_end_point_port}"
