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
        shared_stack: GnosisSafeSharedStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecs_cluster = ecs.Cluster(self, "ErigonCluster", vpc=vpc)

        asg = ecs_cluster.add_capacity(
            "ErigonInstance",
            instance_type=ec2.InstanceType("i3en.3xlarge"),
            associate_public_ip_address=True,
            desired_capacity=1,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
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
                "sudo mkfs -t ext4 /dev/nvme1n1",
                "sudo mount -t ext4 /dev/nvme1n1 /mnt/nvm",
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
            volumes=[
                ecs.Volume(
                    name="ethdata", host=ecs.Host(source_path="/mnt/nvm/ethdata")
                )
            ],
        )

        container = task_definition.add_container(
            "ErigonContainer",
            container_name="erigon",
            image=ecs.ContainerImage.from_registry("thorax/erigon:stable"),
            memory_reservation_mib=1024,
            logging=ecs.AwsLogDriver(
                log_group=log_group,
                stream_prefix="Erigon",
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
            ),
            command=[
                "erigon",
                "--private.api.addr",
                "localhost:9090",
                "--datadir",
                "/data/ethdata",
            ],
            port_mappings=[
                ecs.PortMapping(container_port=30303),  # listner / discovery
                ecs.PortMapping(container_port=30303, protocol=ecs.Protocol.UDP),  # listner / discovery
                ecs.PortMapping(container_port=9090),  # gRPC
            ],
        )

        container.add_mount_points(
            ecs.MountPoint(
                source_volume="ethdata",
                container_path="/data/ethdata",
                read_only=False,
            )
        )

        # rpc_container = task_definition.add_container(
        #     "ErigonRPCContainer",
        #     container_name="erigonrpc",
        #     image=ecs.ContainerImage.from_registry("thorax/erigon:stable"),
        #     memory_reservation_mib=1024,
        #     logging=ecs.AwsLogDriver(
        #         log_group=log_group,
        #         stream_prefix="ErigonRPC",
        #         mode=ecs.AwsLogDriverMode.NON_BLOCKING,
        #     ),
        #     command=[
        #         "rpcdaemon",
        #         "--private.api.addr",
        #         "localhost:9090",
        #         "--datadir",
        #         "/data/ethdata",
        #         "--http.addr",
        #         "0.0.0.0",
        #         "--http.port",
        #         "8545",
        #         "--http.vhosts",
        #         "*",
        #         "--http.corsdomain",
        #         "*",
        #         "--http.api",
        #         "eth,debug,net,trace,web3,erigon",
        #         "--ws",
        #     ],
        #     port_mappings=[
        #         ecs.PortMapping(container_port=8545),  # RPC
        #     ],
        # )

        # rpc_container.add_mount_points(
        #     ecs.MountPoint(
        #         source_volume="ethdata",
        #         container_path="/data/ethdata",
        #         read_only=False,
        #     )
        # )

        service = ecs.Ec2Service(
            self,
            "ErigonService",
            cluster=ecs_cluster,
            task_definition=task_definition,
            desired_count=1,
            enable_execute_command=True,
        )

        # listener = shared_stack.erigon_nlb.add_listener(
        #     "ErigonListener", protocol=elbv2.ApplicationProtocol.HTTP
        # )

        # listener.add_targets(
        #     "Static",
        #     port=80,
        #     targets=[
        #         service.load_balancer_target(
        #             container_name="erigonrpc", container_port=8545
        #         )
        #     ],
        #     health_check=elbv2.HealthCheck(path="/api/", healthy_http_codes="405"),
        # )

        # service.connections.allow_to(shared_stack.erigon_nlb, ec2.Port.all_tcp())
