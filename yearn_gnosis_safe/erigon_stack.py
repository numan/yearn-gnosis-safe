from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_logs as logs
from aws_cdk import core as cdk

from yearn_gnosis_safe.gnosis_safe_shared_stack import GnosisSafeSharedStack


class ErigonEthereumStack(cdk.Stack):
    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        # shared_stack: GnosisSafeSharedStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecs_cluster = ecs.Cluster(self, "ErigonCluster", vpc=vpc)

        asg = ecs_cluster.add_capacity(
            "ErigonInstance",
            instance_type=ec2.InstanceType("i3.xlarge"),
            desired_capacity=1,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            key_name="ethereum-node",
        )

        asg.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "AmazonSSMManagedInstanceCore"
            )
        )

        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            *[
                "sudo mkdir /mnt/nvm/",
                "sudo mkfs -t ext4 /dev/nvme0n1",
                "sudo mount -t ext4 /dev/nvme0n1 /mnt/nvm",
                "sudo mkdir -p /mnt/nvm/ethdata",
                "sudo chown ec2-user:ec2-user /mnt/nvm/ethdata",
            ]
        )
        asg.add_user_data(user_data.render())

        log_group = logs.LogGroup(
            self, "LogGroup", retention=logs.RetentionDays.ONE_MONTH
        )

        task_definition = ecs.Ec2TaskDefinition(
            self,
            "ErigonTaskDefinition",
            network_mode=ecs.NetworkMode.BRIDGE,
            volumes=[
                ecs.Volume(
                    name="ethdata", host=ecs.Host(source_path="/mnt/nvm/ethdata")
                )
            ],
        )

        container = task_definition.add_container(
            "ErigonContainer",
            container_name="erigon",
            image=ecs.ContainerImage.from_asset("docker/erigon"),
            memory_reservation_mib=1024,
            logging=ecs.AwsLogDriver(
                log_group=log_group,
                stream_prefix="Erigon",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            command=[
                "erigon",
                "--private.api.addr",
                "0.0.0.0:9090",
                "--datadir",
                "/data/ethdata",
                "--chain",
                "rinkeby",
                "--healthcheck",
            ],
            port_mappings=[
                ecs.PortMapping(container_port=30303),  # listner / discovery
                ecs.PortMapping(
                    container_port=30303, protocol=ecs.Protocol.UDP
                ),  # listner / discovery
                ecs.PortMapping(container_port=9090),  # gRPC
            ],
            health_check=ecs.HealthCheck(
                command=[
                    "CMD-SHELL",
                    "/usr/local/bin/grpc_health_probe -addr 127.0.0.1:9090 || exit 1",
                ]
            ),
        )

        container.add_mount_points(
            ecs.MountPoint(
                source_volume="ethdata",
                container_path="/data/ethdata",
                read_only=False,
            )
        )

        rpc_container = task_definition.add_container(
            "ErigonRPCContainer",
            container_name="erigonrpc",
            image=ecs.ContainerImage.from_registry("thorax/erigon:latest"),
            memory_reservation_mib=1024,
            logging=ecs.AwsLogDriver(
                log_group=log_group,
                stream_prefix="ErigonRPC",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            command=[
                "rpcdaemon",
                "--private.api.addr",
                "erigon:9090",
                "--http.addr",
                "0.0.0.0",
                "--http.port",
                "8545",
                "--http.vhosts",
                "*",
                "--http.corsdomain",
                "*",
                "--http.api",
                "eth,debug,net,trace,web3,erigon",
                "--verbosity",
                "3",
                "--trace.maxtraces",
                "10000",
                "--rpc.batch.concurrency",
                "6",
            ],
            port_mappings=[
                ecs.PortMapping(container_port=8545),  # RPC
            ],
        )

        dependency = ecs.ContainerDependency(
            container=container, condition=ecs.ContainerDependencyCondition.HEALTHY
        )
        rpc_container.add_container_dependencies(dependency)
        rpc_container.add_link(container, "erigon")

        service = ecs.Ec2Service(
            self,
            "ErigonService",
            cluster=ecs_cluster,
            task_definition=task_definition,
            desired_count=1,
            enable_execute_command=True,
        )

        alb = elbv2.ApplicationLoadBalancer(
            self, "ErigonALB", vpc=vpc, internet_facing=True
        )

        listener = alb.add_listener(
            "ErigonListener", protocol=elbv2.ApplicationProtocol.HTTP, port=8545
        )

        listener.add_targets(
            "RPC",
            protocol=elbv2.ApplicationProtocol.HTTP,
            targets=[
                service.load_balancer_target(
                    container_name="erigonrpc",
                )
            ],
            health_check=elbv2.HealthCheck(
                path="/",
                healthy_http_codes="400,200",
                timeout=cdk.Duration.seconds(60),
                interval=cdk.Duration.seconds(65),
            ),
        )

        # service.connections.allow_to(shared_stack.erigon_nlb, ec2.Port.all_tcp())
