from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import core as cdk
from aws_cdk import aws_elasticloadbalancingv2 as elbv2

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack


class GnosisSafeConfigurationStack(cdk.Stack):
    @property
    def alb(self):
        return self._alb

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        vpc: ec2.IVpc,
        shared_stack: GnosisSafeSharedStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecs_cluster = ecs.Cluster(
            self,
            "GnosisSafeCluster",
            enable_fargate_capacity_providers=True,
            vpc=vpc,
        )

        container_args = {
            "image": ecs.ContainerImage.from_asset("docker/config"),
            "environment": {
                "PYTHONDONTWRITEBYTECODE": "true",
                "DEBUG": "true",
                "ROOT_LOG_LEVEL": "DEBUG",
                "DJANGO_ALLOWED_HOSTS": "*",
                "GUNICORN_BIND_PORT": "8001",
                "DOCKER_NGINX_VOLUME_ROOT": "/nginx",
                "GUNICORN_BIND_SOCKET": "unix:/gunicorn.socket",
                "NGINX_ENVSUBST_OUTPUT_DIR": "/etc/nginx/",
                "POSTGRES_NAME": "postgres",
                "GUNICORN_WEB_RELOAD": "false",
                "DEFAULT_FILE_STORAGE": "django.core.files.storage.FileSystemStorage",
                "CGW_URL": shared_stack.config_alb.load_balancer_dns_name,
                "TRANSACTION_SERVICE_URI": f"http://{shared_stack.transaction_alb.load_balancer_dns_name}",
            },
            "secrets": {
                "SECRET_KEY": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CFG_SECRET_KEY"
                ),
                "DJANGO_SUPERUSER_USERNAME": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CFG_DJANGO_SUPERUSER_USERNAME"
                ),
                "DJANGO_SUPERUSER_PASSWORD": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CFG_DJANGO_SUPERUSER_PASSWORD"
                ),
                "DJANGO_SUPERUSER_EMAIL": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CFG_DJANGO_SUPERUSER_EMAIL"
                ),
                "CGW_FLUSH_TOKEN": ecs.Secret.from_secrets_manager(
                    shared_stack.secrets, "CGW_WEBHOOK_TOKEN"
                ),
                "POSTGRES_USER": ecs.Secret.from_secrets_manager(
                    shared_stack.database.secret, "username"
                ),
                "POSTGRES_PASSWORD": ecs.Secret.from_secrets_manager(
                    shared_stack.database.secret, "password"
                ),
                "POSTGRES_HOST": ecs.Secret.from_secrets_manager(
                    shared_stack.database.secret, "host"
                ),
                "POSTGRES_PORT": ecs.Secret.from_secrets_manager(
                    shared_stack.database.secret, "port"
                ),
            },
        }

        ## Web
        web_task_definition = ecs.FargateTaskDefinition(
            self,
            "SafeConfigurationServiceWeb",
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
            logging=ecs.AwsLogDriver(
                log_group=shared_stack.log_group,
                stream_prefix="Web",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            port_mappings=[ecs.PortMapping(container_port=8001)],
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

        ## Setup LB and redirect traffic to web and static containers

        listener = shared_stack.config_alb.add_listener("Listener", port=80)

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

        ## Permissions

        for service in [web_service]:
            service.connections.allow_to(
                shared_stack.database, ec2.Port.tcp(5432), "RDS"
            )
