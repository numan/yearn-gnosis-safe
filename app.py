#!/usr/bin/env python3
import os

import aws_cdk as cdk

from yearn_gnosis_safe.yearn_gnosis_safe_stack import YearnGnosisSafeStack

app = cdk.App()
environment = cdk.Environment(
    account=os.environ.get("CDK_DEPLOY_ACCOUNT", os.environ["CDK_DEFAULT_ACCOUNT"]),
    region=os.environ.get("CDK_DEPLOY_REGION", os.environ["CDK_DEFAULT_REGION"]),
)

ui_subdomain = os.environ.get("UI_SUBDOMAIN", None)
include_rinkeby = os.environ.get("INCLUDE_RINKEBY", "false").lower() == "true"

config_service_uri = os.environ.get("CONFIG_SERVICE_URI", None)
client_gateway_url = os.environ.get("CLIENT_GATEWAY_URL", None)
mainnet_transaction_gateway_url = os.environ.get("MAINNET_TRANSACTION_GATEWAY_URL", None)
rinkeby_transaction_gateway_url = os.environ.get("RINKEBY_TRANSACTION_GATEWAY_URL", None)

ssl_certificate_arn = os.environ.get("SSL_CERTIFICATE_ARN", None)

environment_name = "production"
prod_stack = YearnGnosisSafeStack(
    app,
    "GnosisSafeStack",
    ui_subdomain=ui_subdomain,
    include_rinkeby=include_rinkeby,
    environment_name=environment_name,
    config_service_uri=config_service_uri,
    client_gateway_url=client_gateway_url,
    mainnet_transaction_gateway_url=mainnet_transaction_gateway_url,
    rinkeby_transaction_gateway_url=rinkeby_transaction_gateway_url,
    ssl_certificate_arn=ssl_certificate_arn,
    env=environment,
)

cdk.Tags.of(prod_stack).add("environment", environment_name)
cdk.Tags.of(prod_stack).add("app", "Gnosis Safe")

app.synth()
