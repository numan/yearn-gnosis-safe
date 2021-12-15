
* [Welcome to Yearn Gnosis Safe!](#welcome-to-yearn-gnosis-safe)
   * [Setting up your local environment](#setting-up-your-local-environment)
   * [Infrastructure](#infrastructure)
   * [Deploying Gnosis Safe](#deploying-gnosis-safe)
      * [Prerequisites](#prerequisites)
      * [1. Create infrastructure for secrets and add secrets](#1-create-infrastructure-for-secrets-and-add-secrets)
      * [2. Build production bundle of the Gnosis Safe UI](#2-build-production-bundle-of-the-gnosis-safe-ui)
      * [3. Create the rest of the Gnosis Safe infrastructure (Client Gateway, Transaction Service, UI, Configuration Service)](#3-create-the-rest-of-the-gnosis-safe-infrastructure-client-gateway-transaction-service-ui-configuration-service)
      * [4. Index transaction data for existing safes](#4-index-transaction-data-for-existing-safes)
   * [Docker Containers](#docker-containers)
      * [Client Gateway](#client-gateway)
      * [Configuration Service](#configuration-service)
      * [Transactions Service](#transactions-service)
      * [Gnosis Safe UI](#gnosis-safe-ui)

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
4. Index transaction data for existing safes

### Prerequisites

Before you start you need to install **AWS CDK CLI** and bootstrap your AWS account:

1. [Prerequisites](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_prerequisites) 
2. [Install AWS CDK Locally](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_install)
3. [Bootstrapping](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html#getting_started_bootstrap)

The infrastructure in this repository requires a VPC with at least one public subnet. If you don't have a VPC that meets this criteria or want to provision a new VPC for this project, you can follow the instructions [here](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-public-private-vpc.html).

To install a self hosted version of Gnosis Safe, you'll also need the following:

1. An Ethereum *Mainnet* node with the [Openethereum trace api](https://openethereum.github.io/JSONRPC-trace-module)
2. An Ethereum *Rinkeby* node with the [Openethereum trace api](https://openethereum.github.io/JSONRPC-trace-module)
3. An [Infura API](https://infura.io/) key
4. An [Etherscan API](https://etherscan.io/apis) key
5. An [Eth Gas Station API](https://docs.ethgasstation.info/#how-to-obtain-an-api-key) key
6. An [Exchange Rate API](https://exchangeratesapi.io/) key

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

The [Gnosis Safe UI](https://github.com/gnosis/safe-react) is part of this GitHub repo as a submodule in the `docker/ui/safe-react` folder. Ensure that the submodule has been initialized:

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

### 4. Index transaction data for existing safes

Indexing happens automatically, however, it can take 12+ hours for indexing to catch up to the most recent transaction. Once indexing is complete, you should be able to add any existing safe. 

## Docker Containers

This project uses the official [Gnosis Safe Docker Images](https://hub.docker.com/u/gnosispm) as a base and applies some modifications to support a self-hosted version.

All customized Dockerfiles can be found in the `docker/` directory.

### Client Gateway

There are no modifications made to the original docker image.

### Configuration Service

Adds a new command to bootstrap the configuration service with configurations that replicate the configurations found on the official [Gnosis Safe Configuration Service](https://safe-config.gnosis.io/).

The bootstrap command is designed to run only if there are no existing configurations.

Also modifies the default container command run by the container to run the bootstrap command on initialization.

### Transactions Service

Installs a new CLI command `reindex_master_copies_with_retry` and a new Gnosis Safe indexer `retryable_index_service` that retries if a JSON RPC call fails during indexing. This was added to make indexing more reliable during initial bootstraping after a new install.

### Gnosis Safe UI

Contains a git submodule with the official [Gnosis Safe UI](https://github.com/gnosis/safe-react). It uses the official Gnosis Safe UI repository to build the production bundle.

Before building a production file, some of the original configuration files are replaced. The current official ui hard codes the url for the configuration and transaction services. The configuration files are replaced to point to the newly deployed configuration and transaction services.

Running `docker/ui/build.sh` will automatically replace the configuration files and build a production bundle.

The UI is the only component that isn't hosted in a docker container. It is hosted as a static website on S3.