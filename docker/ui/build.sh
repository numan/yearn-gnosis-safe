#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

WRENCH="\xf0\x9f\x94\xa7"
FOLDERS="\xf0\x9f\x97\x82"

# TODO install jq, xargs
if [[ -z "$ENVIRONMENT_NAME" ]]; then
    echo "Must provide ENVIRONMENT_NAME in environment" 1>&2
    exit 1
fi

if [[ -z "$AWS_PROFILE" ]]; then
    echo "Must provide AWS_PROFILE in environment" 1>&2
    exit 1
fi

if [[ -z "$AWS_REGION" ]]; then
    export AWS_REGION="us-east-1"
fi


SECRET_ID=$(aws secretsmanager list-secrets --query "SecretList[?Tags[?Key=='environment' && Value=='${ENVIRONMENT_NAME}']]" --filters Key=name,Values=GnosisSharedSecrets --query "SecretList[0].ARN" --output text)

SECRETS=$(aws secretsmanager get-secret-value --secret-id ${SECRET_ID} | jq --raw-output '.SecretString')

# Other variables
export REACT_APP_ENV=${ENVIRONMENT_NAME}
export NODE_ENV=${ENVIRONMENT_NAME}
export REACT_APP_GOOGLE_ANALYTICS=""
export REACT_APP_IPFS_GATEWAY="https://ipfs.io/ipfs"
export REACT_APP_SENTRY_DSN=""
export REACT_APP_INTERCOM_ID=""
export REACT_APP_PORTIS_ID="852b763d-f28b-4463-80cb-846d7ec5806b"
export REACT_APP_FORTMATIC_KEY="pk_test_CAD437AA29BE0A40"
export REACT_APP_COLLECTIBLES_SOURCE="Gnosis"
export REACT_APP_LATEST_SAFE_VERSION="1.3.0"
export REACT_APP_APP_VERSION="3.15.6"
export REACT_APP_SPENDING_LIMIT_MODULE_ADDRESS="0x9e9Bf12b5a66c0f0A7435835e0365477E121B110"

# Secret environment variables
export REACT_APP_ETHGASSTATION_API_KEY=$(echo $SECRETS | jq -r .UI_REACT_APP_ETHGASSTATION_API_KEY | xargs)
export REACT_APP_ETHERSCAN_API_KEY=$(echo $SECRETS | jq -r .UI_REACT_APP_ETHERSCAN_API_KEY | xargs)
export REACT_APP_INFURA_TOKEN=$(echo $SECRETS | jq -r .UI_REACT_APP_INFURA_TOKEN | xargs)
export REACT_APP_SAFE_APPS_RPC_INFURA_TOKEN=$(echo $SECRETS | jq -r .UI_REACT_APP_SAFE_APPS_RPC_INFURA_TOKEN | xargs)

export REACT_APP_SAFE_TRANSACTION_GATEWAY_MAINNET_API_URI=
export REACT_APP_SAFE_TRANSACTION_GATEWAY_RINKEBY_API_URI=
export REACT_APP_SAFE_CLIENT_GATEWAY_API_URI=

while read -r LB_ARN DNS_NAME; do
    IS_TX_MAINNET_LB=$(aws elbv2 describe-tags --resource-arns ${LB_ARN} --query "TagDescriptions[?Tags[?Key=='environment' && Value=='${ENVIRONMENT_NAME}']] && TagDescriptions[?Tags[?Key=='Name' && Value=='Gnosis Transaction Mainnet']]" --output text)
    IS_TX_RINKEBY_LB=$(aws elbv2 describe-tags --resource-arns ${LB_ARN} --query "TagDescriptions[?Tags[?Key=='environment' && Value=='${ENVIRONMENT_NAME}']] && TagDescriptions[?Tags[?Key=='Name' && Value=='Gnosis Transaction Rinkeby']]" --output text)
    IS_CGW_LB=$(aws elbv2 describe-tags --resource-arns ${LB_ARN} --query "TagDescriptions[?Tags[?Key=='environment' && Value=='${ENVIRONMENT_NAME}']] && TagDescriptions[?Tags[?Key=='Name' && Value=='Gnosis Client Gateway']]" --output text)
    echo
    if [[ -n $IS_TX_MAINNET_LB ]]; then
        REACT_APP_SAFE_TRANSACTION_GATEWAY_MAINNET_API_URI="http://${DNS_NAME}/api/v1"
        printf "Setting MAINNET Transaction URI ${ORANGE}${REACT_APP_SAFE_TRANSACTION_GATEWAY_MAINNET_API_URI}${NC}"
    fi
    if [[ -n $IS_TX_RINKEBY_LB ]]; then
        REACT_APP_SAFE_TRANSACTION_GATEWAY_RINKEBY_API_URI="http://${DNS_NAME}/api/v1"
        printf "Setting RINKEBY Transaction URI ${ORANGE}${REACT_APP_SAFE_TRANSACTION_GATEWAY_RINKEBY_API_URI}${NC}"
    fi
    if [[ -n $IS_CGW_LB ]]; then
        REACT_APP_SAFE_CLIENT_GATEWAY_API_URI="http://${DNS_NAME}/v1"
        printf "Setting Client Gateway URI ${ORANGE}${REACT_APP_SAFE_CLIENT_GATEWAY_API_URI}${NC}"
    fi
done <<< "$(aws elbv2 describe-load-balancers --query "LoadBalancers[].{ID:LoadBalancerArn,NAME:DNSName}" --output text)"


printf "\n"

## Override
if [[ -n "$TRANSACTION_GATEWAY_MAINNET_BASE_URI" ]]; then
    printf "Setting MAINNET Transaction URI using ${RED}OVERRIDE ${ORANGE}${TRANSACTION_GATEWAY_MAINNET_BASE_URI}${NC}\n"
    REACT_APP_SAFE_TRANSACTION_GATEWAY_MAINNET_API_URI="${TRANSACTION_GATEWAY_MAINNET_BASE_URI}/api/v1"
fi


if [[ -n "$TRANSACTION_GATEWAY_RINKEBY_BASE_URI" ]]; then
    printf "Setting RINKEBY Transaction URI using ${RED}OVERRIDE ${ORANGE}${TRANSACTION_GATEWAY_RINKEBY_BASE_URI}${NC}\n"
    REACT_APP_SAFE_TRANSACTION_GATEWAY_RINKEBY_API_URI="${TRANSACTION_GATEWAY_RINKEBY_BASE_URI}/api/v1"
fi


if [[ -n "$CLIENT_GATEWAY_BASE_URI" ]]; then
    printf "Setting Client Gateway URI using ${RED}OVERRIDE ${ORANGE}${CLIENT_GATEWAY_BASE_URI}${NC}\n"
    REACT_APP_SAFE_CLIENT_GATEWAY_API_URI="${CLIENT_GATEWAY_BASE_URI}/v1"
fi

printf "\n"

if [[ -z REACT_APP_SAFE_TRANSACTION_GATEWAY_MAINNET_API_URI ]]; then
    echo "REACT_APP_SAFE_TRANSACTION_GATEWAY_MAINNET_API_URI not found" 1>&2
    exit 1
fi


if [[ -z REACT_APP_SAFE_TRANSACTION_GATEWAY_RINKEBY_API_URI ]]; then
    echo "REACT_APP_SAFE_TRANSACTION_GATEWAY_RINKEBY_API_URI not found" 1>&2
    exit 1
fi

if [[ -z REACT_APP_SAFE_CLIENT_GATEWAY_API_URI ]]; then
    echo "REACT_APP_SAFE_CLIENT_GATEWAY_API_URI not found" 1>&2
    exit 1
fi

export PUBLIC_URL="/"

printf "${WRENCH} ${GREEN}Building UI${NC}\n"

printf "${WRENCH} ${GREEN}Replace server configurations ${NC}\n"
cp configs/* ./safe-react/src/config/networks/

printf "${WRENCH} ${GREEN}Creating an optimized production build...${NC}\n"
# TODO: Do a yarn install
yarn --cwd safe-react build

printf "${FOLDERS} ${GREEN}Moving UI build for docker${NC}\n"
BUILD_DIRECTORY=build_${ENVIRONMENT_NAME}
rm -rf ./builds/${BUILD_DIRECTORY}
mv ./safe-react/build ./builds/${BUILD_DIRECTORY}

printf "${FOLDERS} ${GREEN}Reverting configuration changes${NC}\n"
git submodule foreach git reset --hard
