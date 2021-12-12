
# Welcome to Yearn Gnosis Safe!

This repository contains Infrastructure as Code (IaC) for a self-hosted version of
Gnosis Safe on AWS.

The infrastructure is defined using **[AWS Cloud Development Kit (AWS CDK)](https://aws.amazon.com/cdk/)**.
AWS CDK is an open source software development framework to define your cloud application resources using
familiar programming languages.

These definitions can then be synthesized to AWS CloudFormation Templates which can be deployed AWS.

## Setting up your local environment

Clone this repository.

It is best practice to use an isolated environment when working with this project.
To manually create a virtualenv virtual environment on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

## Infrastructure

The following diagram provides a high level overview of the infrastructure that this repository deploys:

![Infrastructure Diagram](./assets/SelfHostedGnosisSafe.png)

[Source](https://drive.google.com/file/d/1gySv-RDkNYCQkVAr7eyniQx7Sl3N8j-7/view?usp=sharing)

1. The production bundle is deployed to an S3 bucket. You should be able to find the URL of the frontend UI by looking at the `Bucket website endpoint` in the `Static website hosting` section of the bucket's properties.
2. The frontend UI uses blockchain nodes to power some of the functionality. You can use a service such as Infura or Alchemy.
3. The UI performs most of its functionality by communicating with the Client Gateway.
4. The Client Gateway retrieves information about safes from the transaction service. There is a transaction service deployed for Mainnet and Rinkeby.
5. The Client Gateway also relies on the configuration service to determine which nodes and services to use for each network.
6. Secrets store stores credentials for all the different services.
7. The transaction service monitors Ethereum nodes for new blocks and inspects transactions with the `trace` API to index new safe related events. 


## Deploying Gnosis Safe

Deploying can be summarized in the following steps:

1. Create infrastructure for secrets and add secrets
2. Build production bundle of the Gnosis Safe UI
3. Create the rest of the Gnosis Safe infrastructure (Client Gateway, Transaction Service, UI, Configuration Service)
4. Bootstrap transaction data for existing safes

### Prerequisites

Before you start you need to install **AWS CDK CLI** and bootstrap your AWS account:

1. [Prerequisites](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_prerequisites) 
2. [Install AWS CDK Locally](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install)
3. [Bootstrapping](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_bootstrap)

The infrastructure in this repository requires a VPC with at least one public subnet. If you don't have a VPC that meets this criteria or want to provision a new VPC for this project, you can follow the instructions [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-public-private-vpc.html).

To install a self hosted version of Gnosis Safe, you'll also need the following:

1. An Ethereum *Mainnet* node with the [Openethereum trace api](https://openethereum.github.io/JSONRPC-trace-module)
2. An Ethereum *Rinkeby* node with the [Openethereum trace api](https://openethereum.github.io/JSONRPC-trace-module)
3. An (Infura API)[https://infura.io/] key
4. An (Etherscan API)[https://etherscan.io/apis] key
5. An (Eth Gas Station API)[https://docs.ethgasstation.info/#how-to-obtain-an-api-key] key
6. An (Exchange Rate API)[https://exchangeratesapi.io/] key

### 1. Create infrastructure for secrets and add secrets

Use the **AWS CDK CLI** to deploy the shared infrastructure including a Secrets Vault where all sensitive secrets will be stored:

```bash
$ CDK_DEPLOY_ACCOUNT="111111111111" CDK_DEPLOY_REGION="us-east-1" cdk deploy GnosisSafeStack/GnosisShared --require-approval never
```

> `CDK_DEPLOY_ACCOUNT` and `CDK_DEPLOY_REGION` define the account and region you're deploying the infrastructure to respectively

The deployment should create a shared secrets vault for all your secrets as well 2 secrets vaults for Postgres database credentials: one for the *Rinkeby Transaction Service* and one for the *Mainnet Transaction Service*.

> You can distinguish the different vaults by inspecting their tags. The Shared Secrets vault will have a `aws:cloudformation:logical-id` that starts with `GnosisSharedSecrets`

> Mainnet Postgres database credentials secrets vault will have a `aws:cloudformation:logical-id` that starts with `GnosisSafeStackGnosisSharedMainnetTxDatabaseSecret`

> Rinkeby Postgres database credentials secrets vault will have a `aws:cloudformation:logical-id` that starts with `GnosisSafeStackGnosisSharedRinkebyTxDatabaseSecret`


Fill out the following credentials in the Shared Secrets vault:

  1. TX_DATABASE_URL_MAINNET - Use the Mainnet Postgres database credentials and create a URL using the following template: `postgres://postgres:<PASSWORD>@<URL>:5432/postgres`
  2. TX_ETHEREUM_TRACING_NODE_URL_MAINNET - An Ethereum Mainnet node URL that has access to the `trace` API
  3. TX_ETHEREUM_NODE_URL_MAINNET - An Ethereum Mainnet node URL. Can be the same as `TX_ETHEREUM_TRACING_NODE_URL_MAINNET`
  4. TX_DJANGO_SECRET_KEY_MAINNET - Generate randomly using `openssl rand -base64 18`
  5. TX_DATABASE_URL_RINKEBY - Use the Rinkeby Postgres database credentials and create a URL using the following template: `postgres://postgres:<PASSWORD>@<URL>:5432/postgres`
  6. TX_ETHEREUM_TRACING_NODE_URL_RINKEBY - An Ethereum Rinkeby node URL that has access to the `trace` API
  7. TX_ETHEREUM_NODE_URL_RINKEBY - An Ethereum Rinkeby node URL. Can be the same as `TX_ETHEREUM_TRACING_NODE_URL_RINKEBY`
  8. TX_DJANGO_SECRET_KEY_RINKEBY - Generate randomly using `openssl rand -base64 18`
  9. UI_REACT_APP_INFURA_TOKEN - An Infura API token to use in the Frontend UI
  10. UI_REACT_APP_SAFE_APPS_RPC_INFURA_TOKEN - An Infura API token that you want to use for RPC calls. Can be the same as `UI_REACT_APP_INFURA_TOKEN`.
  11. CFG_DJANGO_SUPERUSER_EMAIL - The email address for the superuser of the Configuration service
  12. CFG_DJANGO_SUPERUSER_PASSWORD - The password for the superuser of the Configuration service. Randomly generate using `openssl rand -base64 18`.
  13. CFG_DJANGO_SUPERUSER_USERNAME - The username for the superuser of the Configuration service
  14. CFG_SECRET_KEY - Generate randomly using `openssl rand -base64 18`
  15. CGW_EXCHANGE_API_KEY - Your Exchange Rate API key
  16. UI_REACT_APP_ETHERSCAN_API_KEY - Your Etherscan API key
  17. CGW_ROCKET_SECRET_KEY - Generate randomly using `date |md5 | head -c24; echo`
  18. UI_REACT_APP_ETHGASSTATION_API_KEY - Your Eth Gas Station API key
  19. CGW_WEBHOOK_TOKEN - Generate randomly using `date |md5 | head -c24; echo`
  20. password - Not used. Leave as is.

  ### 2. Build production bundle of the Gnosis Safe UI

The (Gnosis Safe UI)[https://github.com/gnosis/safe-react] is part of this GitHub repo as a submodule in the `docker/ui/safe-react` folder. Ensure that the submodule has been initialized:

```bash
$ git submodule update --init --recursive
```

To build the production bundle of the Gnosis Safe UI, use the build script in the `docker/ui` directory:

```bash
$ cd docker/ui
$ ENVIRONMENT_NAME=production ./build.sh
$ ../..
```

### 3. Create the rest of the Gnosis Safe infrastructure (Client Gateway, Transaction Service, UI, Configuration Service)

Deploy the rest of the Gnosis Safe infrastructure:

```bash
$ CDK_DEPLOY_ACCOUNT="111111111111" CDK_DEPLOY_REGION="us-east-1" cdk deploy --all --require-approval never
```

### 4. Bootstrap transaction data for existing safes

You can't import existing safes until the transaction service has indexed historical safes. To initiate indexing, you have to connect to the transaction service web container.

Find the **ECS Fargate** cluster and task id of the mainnet transaction service. The cluster name should start with **GnosisSafeStackGnosisTxMainnet**. Find the task within the cluster running the `web` container.

To connect to the container, use the following AWS CLI command:

```bash
$ aws ecs execute-command  \
    --region us-east-1 \
    --cluster <CLUSTER NAME> \
    --task <TASK ID> \
    --container web \
    --command "/bin/bash" \
    --interactive
```

Once connected to the container, you can start the re-indexing process by using the following command:

```bash
$ nohup python manage.py reindex_master_copies_with_retry --address ADDRESS1 ADDRESS2 --from-block-number BLOCK_NUMBER --block-process-limit 250 &
```

For example, to index a safe at `0xfeb4acf3df3cdea7399794d0869ef76a6efaff52` find the block the safe was created in on [Etherscan](https://etherscan.io/tx/0x3e697d51231aea892d410743c15f3feebcdc8a3f2602f8830d02d7dd5f52cec0) and issue the following command:

```bash
$ nohup python manage.py reindex_master_copies_with_retry --address 0xfeb4acf3df3cdea7399794d0869ef76a6efaff52 --from-block-number 10701802 --block-process-limit 250 &
```

To index multiple safes, find the a block number before all the safes you're interested in were created and issue the following command:

```bash
$ nohup python manage.py reindex_master_copies_with_retry --address 0xfeb4acf3df3cdea7399794d0869ef76a6efaff52 0x3305b8bc94d29f08277ae525e9335c531db97372ada8f80a5cb553d46399d8c8 --from-block-number 10701000 --block-process-limit 250 &
```

To index ALL safes, use the following command:

```bash
$ nohup python manage.py reindex_master_copies_with_retry --from-block-number 7457550 --block-process-limit 250 &
```

`7457553` is the block Version 1.0.0 of the Gnosis Safe contract was deployed, so the above command indexes all Gnosis Safe contracts.

This should start the re-indexing process. You can track the progress by following the output log:

```bash
$ tail -f nohup.out
```

> **NOTE:** The indexing process can take several hours to run. The less safes you include, the faster the indexing process will run.

> **NOTE:** If you want to index all safes, you'll want to upgrade the transaction service database, redis cache and increase the number of workers.

> **NOTE:** The following steps can also be use on the Rinkeby transaction service.