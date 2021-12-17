from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticache as elasticache
from aws_cdk import core as cdk


class RedisStack(cdk.Construct):
    @property
    def connections(self):
        return self._connections

    def __init__(self, scope: cdk.Construct, id: str, vpc: ec2.IVpc, cache_node_type: str="cache.t3.small") -> None:
        super().__init__(scope, id)

        sg_elasticache = ec2.SecurityGroup(
            self,
            "RedisServerSG",
            vpc=vpc,
            allow_all_outbound=True,
            description="security group for redis",
        )
        cdk.Tags.of(sg_elasticache).add("Name", "redis-server")

        sg_elasticache.add_ingress_rule(
            peer=sg_elasticache,
            connection=ec2.Port.all_tcp(),
            description="default-redis-server",
        )

        self._connections = ec2.Connections(
            security_groups=[sg_elasticache], default_port=ec2.Port.tcp(6379)
        )

        elasticache_subnet_group = elasticache.CfnSubnetGroup(
            self,
            "RedisSubnetGroup",
            description="subnet group for redis",
            subnet_ids=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE).subnet_ids
            + vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnet_ids,
        )

        redis_param_group = elasticache.CfnParameterGroup(
            self,
            "RedisParamGroup",
            cache_parameter_group_family="redis5.0",
            description="parameter group for redis5.0",
            properties={
                "databases": "256",  # database: 16 (default)
                # "tcp-keepalive": "0",  # tcp-keepalive: 300 (default)
                # "maxmemory-policy": "volatile-ttl",  # maxmemory-policy: volatile-lru (default)
            },
        )


        redis_with_replicas = elasticache.CfnReplicationGroup(
            self,
            "RedisCacheWithReplicas",
            cache_node_type=cache_node_type,
            engine="redis",
            engine_version="5.0.5",
            snapshot_retention_limit=3,
            snapshot_window="19:00-21:00",
            preferred_maintenance_window="mon:21:00-mon:22:30",
            automatic_failover_enabled=True,
            auto_minor_version_upgrade=True,
            multi_az_enabled=True,
            replication_group_description="redis with replicas",
            replicas_per_node_group=1,
            cache_parameter_group_name=redis_param_group.ref,
            cache_subnet_group_name=elasticache_subnet_group.ref,
            security_group_ids=[sg_elasticache.security_group_id],
            tags=[
                cdk.CfnTag(key="Name", value="redis-with-replicas"),
                cdk.CfnTag(key="desc", value="primary-replica redis"),
            ],
        )
        redis_with_replicas.add_depends_on(elasticache_subnet_group)

        self.cluster = redis_with_replicas
