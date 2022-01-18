import os

from chains.models import Chain, GasPrice, Feature
from django.core.management.base import BaseCommand
from safe_apps.models import Provider, SafeApp

TRANSACTION_SERVICE_MAINNET_URI = os.environ.get(
    "TRANSACTION_SERVICE_MAINNET_URI", "https://safe-transaction.mainnet.gnosis.io"
)
TRANSACTION_SERVICE_RINKEBY_URI = os.environ.get(
    "TRANSACTION_SERVICE_RINKEBY_URI", "https://safe-transaction.mainnet.gnosis.io"
)
VPC_TRANSACTION_SERVICE_MAINNET_URI = (
    "http://mainnet-safe-transaction-web.safe.svc.cluster.local"
)


class Command(BaseCommand):
    help = "Bootstrap configuration data"

    def handle(self, *args, **options):
        Chain.objects.all().delete()
        GasPrice.objects.all().delete()
        Provider.objects.all().delete()
        SafeApp.objects.all().delete()

        self._bootstrap_features()

        if Chain.objects.count() == 0:
            self._bootstrap_chain()
        if SafeApp.objects.count() == 0:
            self._bootstrap_safe_apps()

    def _bootstrap_features(self):
        self._feature_contract_interaction, _ = Feature.objects.get_or_create(key="CONTRACT_INTERACTION")
        self._feature_domain_lookup, _ = Feature.objects.get_or_create(key="DOMAIN_LOOKUP")
        self._feature_eip1559, _ = Feature.objects.get_or_create(key="EIP1559")
        self._feature_erc721, _ = Feature.objects.get_or_create(key="ERC721")
        self._feature_safe_apps, _ = Feature.objects.get_or_create(key="SAFE_APPS")
        self._feature_safe_tx_gas_optional, _ = Feature.objects.get_or_create(key="SAFE_TX_GAS_OPTIONAL")
        self._feature_spending_limit, _ = Feature.objects.get_or_create(key="SPENDING_LIMIT")

    def _bootstrap_safe_apps(self):
        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmQ3w2ezp2zx3u2LYQHyuNzMrLDJFjyL1rjAFTjNMcQ4cK",
            name="Aave",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmQ3w2ezp2zx3u2LYQHyuNzMrLDJFjyL1rjAFTjNMcQ4cK/aave.svg",
            description="Lend and borrow straight from your Gnosis Safe",
            chain_ids=[1],
            provider=Provider.objects.create(url="https://aave.com", name="Aave"),
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmQovvfYYMUXjZfNbysQDUEXR8nr55iJRwcYgJQGJR7KEA",
            name="OpenZeppelin",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmQovvfYYMUXjZfNbysQDUEXR8nr55iJRwcYgJQGJR7KEA/openzeppelin.png",
            description="Securely manage and monitor your Ethereum project.",
            chain_ids=[1, 4],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmT96aES2YA9BssByc6DVizQDkofmKRErs8gJyqWipjyS8",
            name="Mushrooms Finance",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmT96aES2YA9BssByc6DVizQDkofmKRErs8gJyqWipjyS8/logo.png",
            description="Mushrooms Finance is a yield aggregator with focus on seeking sustainable profit",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmTa21pi77hiT1sLCGy5BeVwcyzExUSp2z7byxZukye8hr",
            name="PoolTogether",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmTa21pi77hiT1sLCGy5BeVwcyzExUSp2z7byxZukye8hr/pool-together.png",
            description="No-loss lotteries on your Gnosis Safe",
            chain_ids=[1, 4],
            provider=Provider.objects.create(
                url="https://avolabs.io/", name="Avo Labs"
            ),
        )

        balancer_provider = Provider.objects.create(
            url="https://balancer.finance", name="Balancer Labs"
        )
        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmVaxypk2FTyfcTS9oZKxmpQziPUTu2VRhhW7sso1mGysf",
            name="Balancer Pool Management",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmVaxypk2FTyfcTS9oZKxmpQziPUTu2VRhhW7sso1mGysf/logo512.png",
            description="Manage liquidity on Balancer from your Gnosis Safe",
            chain_ids=[1],
            provider=balancer_provider,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/Qmde8dsa9r8bB59CNGww6LRiaZABuKaJfuzvu94hFkatJC",
            name="Lido Staking",
            icon_url="https://cloudflare-ipfs.com/ipfs/Qmde8dsa9r8bB59CNGww6LRiaZABuKaJfuzvu94hFkatJC/logo.svg",
            description="Lido is the liquid staking solution for Ethereum.",
            chain_ids=[1],
            provider=Provider.objects.create(url="https://lido.fi", name="Lido"),
        )

        SafeApp.objects.create(
            url="https://safe-cmm.gnosis.io",
            name="Gnosis Custom Market Maker",
            icon_url="https://safe-cmm.gnosis.io/img/appIcon.svg",
            description="Allows you to deploy, withdraw and manage your custom market maker strategies",
            chain_ids=[4, 100],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmREcCtsynyrfa4H5bJUJH6sVV1QKygt8M9NNB6dH4Rcm1",
            name="Balancer Exchange",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmREcCtsynyrfa4H5bJUJH6sVV1QKygt8M9NNB6dH4Rcm1/logo512.png",
            description="Exchange tokens using the Balancer DEX",
            chain_ids=[1],
            provider=balancer_provider,
        )

        SafeApp.objects.create(
            url="https://curve.fi",
            name="Curve",
            icon_url="https://curve.fi/logo-square.svg",
            description="Decentralized exchange liquidity pool designed for extremely efficient stablecoin trading and low-risk income for liquidity providers",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.defisaver.com",
            name="DeFi Saver",
            icon_url="https://app.defisaver.com//assets/icons/icon-transparent.svg",
            description="The next generation DeFi management dashboard",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://furucombo.app",
            name="Furucombo",
            icon_url="https://furucombo.app/apple-touch-icon.png",
            description="Create all kinds of DeFi combo.",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://paraswap.io",
            name="ParaSwap",
            icon_url="https://paraswap.io/paraswap.svg",
            description="ParaSwap allows dApps and traders to get the best DEX liquidity by aggregating multiple markets and offering the best rates",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.reflexer.finance",
            name="Reflexer",
            icon_url="https://app.reflexer.finance/logo512.png",
            description="Volatility dampened synthetic instruments",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://stakewise.io",
            name="StakeWise",
            icon_url="https://stakewise.io/logo192.png",
            description="Stake your ETH and manage capital flexibly with the principal and yield tokens.",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmWZDNujzAHeALnzAvmT975TejAmwWmYTpVqgZrexBAVrt",
            name="Liquity Frontend",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmWZDNujzAHeALnzAvmT975TejAmwWmYTpVqgZrexBAVrt/logo256.png",
            description="Simple frontend with high kickback rate, hosted on Arweave and ENS for maximal decentralisation.",
            chain_ids=[1, 4],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://bridge.xdaichain.com",
            name="xDai Bridge",
            icon_url="https://bridge.xdaichain.com/logo.svg",
            description="App that allows you to bridge Dai to xDai and vice versa",
            chain_ids=[1, 100],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://apps.gnosis-safe.io/tx-builder/",
            name="Transaction Builder",
            icon_url="https://apps.gnosis-safe.io/tx-builder/tx-builder.png",
            description="Compose custom contract interactions and batch them into a single transaction",
            chain_ids=[1, 4, 56, 100, 137, 246, 42161, 73799],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://mstable.app",
            name="mStable",
            icon_url="https://mstable.app/assets/icons/mstable-logo.svg",
            description="mStable unites stablecoins, lending and swapping into one standard.",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.dhedge.org/",
            name="dHEDGE",
            icon_url="https://app.dhedge.org/logo.svg",
            description="Decentralized asset management",
            chain_ids=[1, 137],
            provider=Provider.objects.create(
                url="https://www.dhedge.org/", name="dHEDGE"
            ),
        )

        SafeApp.objects.create(
            url="https://app.aave.com",
            name="Aave v2",
            icon_url="https://app.aave.com/aave.svg",
            description="Non-custodial liquidity protocol to earn interest on deposits and borrow",
            chain_ids=[1, 137],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://apps.gnosis-safe.io/compound/",
            name="Compound",
            icon_url="https://apps.gnosis-safe.io/compound/Compound.png",
            description="Money markets on the Ethereum blockchain",
            chain_ids=[1, 4],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmSpfd5UwhUBZxKouqSsY3bFynyDy6sToVLigLwSWRms9s",
            name="Gnosis Auction Starter",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmSpfd5UwhUBZxKouqSsY3bFynyDy6sToVLigLwSWRms9s/logo.svg",
            description="Safe app to start new auctions on Gnosis Auction",
            chain_ids=[1, 4, 100, 137],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://staking.synthetix.io/",
            name="Synthetix",
            icon_url="https://staking.synthetix.io/images/synthetix-logo.svg",
            description="A dApp for SNX holders to earn rewards through staking",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://apps.gnosis-safe.io/wallet-connect",
            name="WalletConnect",
            icon_url="https://apps.gnosis-safe.io/wallet-connect/wallet-connect.svg",
            description="Connect your Safe to any dApp that supports WalletConnect",
            chain_ids=[1, 4, 56, 100, 137, 246, 73799, 42161],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.ens.domains/",
            name="ENS - Ethereum Name Service",
            icon_url="https://app.ens.domains/android-chrome-144x144.png",
            description="Decentralised naming for wallets, websites, & more.",
            chain_ids=[4],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmeXrUW8fQE45GufCvseBtFmJjwrEzxjzNgEL1SSy8hx5Z",
            name="Sablier",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmeXrUW8fQE45GufCvseBtFmJjwrEzxjzNgEL1SSy8hx5Z/logo.svg",
            description="Stream money with Sablier",
            chain_ids=[1, 4, 56, 137],
            provider=Provider.objects.create(
                url="https://sablier.finance", name="Sablier"
            ),
        )

        SafeApp.objects.create(
            url="https://app.zerion.io",
            name="Zerion",
            icon_url="https://app.zerion.io//logo.svg",
            description="Zerion — Invest in DeFi from one place",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmTvrLwJtyjG8QFHgvqdPhcV5DBMQ7oZceSU4uvPw9vQaj",
            name="Idle v4",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmTvrLwJtyjG8QFHgvqdPhcV5DBMQ7oZceSU4uvPw9vQaj/logo.svg",
            description="Always the best yield, with no effort",
            chain_ids=[1, 4],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://oasis.app",
            name="Oasis Borrow",
            icon_url="https://oasis.app/static/img/logo.svg",
            description="Generate Dai on Oasis using crypto as your collateral",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.dodoex.io",
            name="DODO",
            icon_url="https://app.dodoex.io/DODO.svg",
            description="DODO - Your on-chain liquidity provider.",
            chain_ids=[1, 4, 56, 137],
            provider=Provider.objects.create(url="https://dodoex.io/", name="DODO"),
        )

        SafeApp.objects.create(
            url="https://invoicing.request.network/",
            name="Request Invoicing",
            icon_url="https://invoicing.request.network/logo512.png",
            description="The easiest way to get your invoices paid in crypto",
            chain_ids=[1, 4],
            provider=Provider.objects.create(
                url="https://request.network", name="Request"
            ),
        )

        SafeApp.objects.create(
            url="https://app.uniswap.org",
            name="Uniswap",
            icon_url="https://app.uniswap.org/images/256x256_App_Icon_Pink.svg",
            description="Swap or provide liquidity on the Uniswap Protocol",
            chain_ids=[1, 3, 4, 10, 42, 420],
            provider=Provider.objects.create(url="https://uniswap.org", name="Uniswap"),
        )

        SafeApp.objects.create(
            url="https://quickswap.exchange/",
            name="QuickSwap",
            icon_url="https://quickswap.exchange/logo_circle.png",
            description="QuickSwap",
            chain_ids=[137],
            provider=Provider.objects.create(
                url="https://quickswap.exchange", name="QuickSwap"
            ),
        )

        SafeApp.objects.create(
            url="https://armor.fi/",
            name="Armor.Fi",
            icon_url="https://armor.fi/armor-logo.svg",
            description="Smart DeFi Asset Coverage",
            chain_ids=[1],
            provider=Provider.objects.create(url="https://armor.fi", name="Armor.Fi"),
        )

        SafeApp.objects.create(
            url="https://app.sushi.com/",
            name="Sushi",
            icon_url="https://app.sushi.com/_next/image?url=%2Flogo.png&w=64&q=75",
            description="Be a DeFi Chef with Sushi. Swap, earn, stack yields, lend, borrow, leverage all on one decentralized, community driven platform.",
            chain_ids=[1, 43113, 56, 42220, 250, 128, 137, 66, 100],
            provider=Provider.objects.create(
                url="https://sushi.com/", name="SushiSwap"
            ),
        )

        SafeApp.objects.create(
            url="https://tac.dappstar.io/",
            name="Token Allowance Checker",
            icon_url="https://tac.dappstar.io/logo.svg",
            description="Manage your token approvals",
            chain_ids=[1],
            provider=Provider.objects.create(
                url="https://github.com/TripleSpeeder", name="Michael Bauer"
            ),
        )

        SafeApp.objects.create(
            url="https://apps.gnosis-safe.io/drain-safe",
            name="Drain Account",
            icon_url="https://apps.gnosis-safe.io/drain-safe/logo.svg",
            description="Transfer all your Safe assets in a single transaction",
            chain_ids=[1, 4],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.1inch.io",
            name="1inch Network",
            icon_url="https://app.1inch.io/assets/images/1inch_logo_without_text.svg",
            description="The most efficient defi aggregator",
            chain_ids=[1, 56, 137],
            provider=Provider.objects.create(
                url="https://1inch.exchange", name="1inch corporation"
            ),
        )

        SafeApp.objects.create(
            url="https://defi.instadapp.io/",
            name="Instadapp",
            icon_url="https://defi.instadapp.io/android-chrome-512x512.png",
            description="The Most Powerful DeFi Management Platform",
            chain_ids=[1],
            provider=Provider.objects.create(
                url="https://instadapp.io/", name="InstaDApp Labs LLC"
            ),
        )

        SafeApp.objects.create(
            url="https://app.enzyme.finance",
            name="Enzyme Finance",
            icon_url="https://app.enzyme.finance/logo.svg",
            description="Onchain Asset Management",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://stakedao.org",
            name="StakeDAO",
            icon_url="https://stakedao.org/images/logo.svg",
            description="Effortless ways to grow your crypto",
            chain_ids=[1, 137, 43114],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://yearn.finance/",
            name="yearn.finance",
            icon_url="https://yearn.finance/icon_192x192.png",
            description="Put your assets to work.",
            chain_ids=[1],
            provider=Provider.objects.create(
                url="https://yearn.finance/", name="yearn.finance"
            ),
        )

        SafeApp.objects.create(
            url="https://cloudflare-ipfs.com/ipfs/QmXwgRkaVzWmTTT9p3iTzQ5MkGHmqtoMFfJvjF15zGtXD6/",
            name="CSV Airdrop",
            icon_url="https://cloudflare-ipfs.com/ipfs/QmXwgRkaVzWmTTT9p3iTzQ5MkGHmqtoMFfJvjF15zGtXD6//logo.svg",
            description="Upload your CSV transfer file to send arbitrarily many tokens of various amounts to a list of recipients.",
            chain_ids=[1, 4, 100, 56, 137],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.barnbridge.com",
            name="BarnBridge",
            icon_url="https://app.barnbridge.com/logo.svg",
            description="Risk Tokenizing Protocol",
            chain_ids=[1, 137],
            provider=Provider.objects.create(
                url="https://barnbridge.com/", name="BarnBridge"
            ),
        )

        SafeApp.objects.create(
            url="https://ousd.com/",
            name="Origin Dollar",
            icon_url="https://ousd.com/logo.svg",
            description="The first stablecoin that earns a yield while it's still in your wallet",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://dapp.daohaus.club/",
            name="DAOhaus",
            icon_url="https://dapp.daohaus.club/images/icons/icon-512x512.png",
            description="DAOhaus is a no code platform for Moloch DAOs.",
            chain_ids=[1, 4, 137, 100],
            provider=None,
        )
        SafeApp.objects.create(
            url="https://app.superfluid.finance/",
            name="Superfluid",
            icon_url="https://app.superfluid.finance/icons/icon-96x96.png",
            description="Superfluid is a new Ethereum Protocol that extends Ethereum tokens to include novel functionalities. Superfluid enables functionalities like money streaming and reward distribution.",
            chain_ids=[137],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://gnosis-zodiac-app.netlify.app/",
            name="Zodiac",
            icon_url="https://gnosis-zodiac-app.netlify.app/zodiac-app-logo.png",
            description="The expansion pack for DAOs",
            chain_ids=[1, 4, 100, 137],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://apy.plasma.finance",
            name="0xPlasma Finance",
            icon_url="https://apy.plasma.finance/logo.svg",
            description="Cross-chain DeFi & DEX aggregator, farming, asset management, fiat on-ramp",
            chain_ids=[1, 56, 137],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://www.sorbet.finance/",
            name="Sorbet Finance",
            icon_url="https://www.sorbet.finance/sorbet.png",
            description="DeFi's sweetest automated trading & liquidity management application for UniswapV2, PancakeSwap, TraderJoe, and Quickswap. Powered by Gelato Network. Ethereum, BSC, Avalanche & Polygon.",
            chain_ids=[1],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.insurace.io/",
            name="InsurAce",
            icon_url="https://app.insurace.io/logo.svg",
            description="Entry to the products and services InsurAce provides to secure your DeFi journey.",
            chain_ids=[1, 137, 56],
            provider=None,
        )

        SafeApp.objects.create(
            url="https://app.bancor.network/",
            name="Bancor Network",
            icon_url="https://app.bancor.network/logo512.png",
            description="Bancor Safe Staking",
            chain_ids=[1, 3],
            provider=None,
        )

    def _bootstrap_chain(self):

        chain = Chain.objects.create(
            name="Ethereum",
            id="1",
            description="The main Ethereum network",
            short_name="eth",
            l2=False,
            rpc_authentication=Chain.RpcAuthentication.API_KEY_PATH,
            rpc_uri="https://mainnet.infura.io/v3/",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.API_KEY_PATH,
            safe_apps_rpc_uri="https://mainnet.infura.io/v3/",
            public_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            public_rpc_uri="https://cloudflare-eth.com",
            block_explorer_uri_address_template="https://etherscan.io/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://etherscan.io/tx/{{txHash}}",
            block_explorer_uri_api_template="https://api.etherscan.io/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="Ether",
            currency_symbol="ETH",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/1/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#001428",
            theme_background_color="#E8E7E6",
            ens_registry_address="0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e",
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_domain_lookup.chains.add(chain)
        self._feature_eip1559.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)
        self._feature_spending_limit.chains.add(chain)

        chain = Chain.objects.create(
            name="xDai",
            id="100",
            description="",
            short_name="xdai",
            l2=True,
            rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            rpc_uri="https://rpc.xdaichain.com/oe-only/",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            safe_apps_rpc_uri="https://rpc.xdaichain.com/oe-only/",
            public_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            public_rpc_uri="https://rpc.xdaichain.com/oe-only/",
            block_explorer_uri_address_template="https://blockscout.com/xdai/mainnet/address/{{address}}/transactions",
            block_explorer_uri_tx_hash_template="https://blockscout.com/xdai/mainnet/tx/{{txHash}}/",
            block_explorer_uri_api_template="https://blockscout.com/poa/xdai/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="xDai",
            currency_symbol="XDAI",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/100/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#48A9A6",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_eip1559.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)
        self._feature_spending_limit.chains.add(chain)

        chain = Chain.objects.create(
            name="Polygon Matic",
            id="137",
            description="L2 chain (MATIC)",
            short_name="matic",
            l2=True,
            rpc_authentication=Chain.RpcAuthentication.API_KEY_PATH,
            rpc_uri="https://polygon-mainnet.infura.io/v3/",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.API_KEY_PATH,
            safe_apps_rpc_uri="https://polygon-mainnet.infura.io/v3/",
            public_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            public_rpc_uri="https://polygon-rpc.com",
            block_explorer_uri_address_template="https://polygonscan.com/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://polygonscan.com/tx/{{txHash}}",
            block_explorer_uri_api_template="https://api.polygonscan.com/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="Matic",
            currency_symbol="MATIC",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/137/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#8B50ED",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)

        chain = Chain.objects.create(
            name="Binance",
            id="56",
            description="",
            short_name="bnb",
            l2=True,
            rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            rpc_uri="https://bsc-dataseed.binance.org/",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            safe_apps_rpc_uri="https://bsc-dataseed.binance.org/",
            public_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            public_rpc_uri="https://bsc-dataseed.binance.org/",
            block_explorer_uri_address_template="https://bscscan.com/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://bscscan.com/tx/{{txHash}}",
            block_explorer_uri_api_template="https://api.bscscan.com/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="BNB",
            currency_symbol="BNB",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/56/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#fcc323",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)
        self._feature_spending_limit.chains.add(chain)

        chain = Chain.objects.create(
            name="Energy Web",
            id="246",
            description="",
            short_name="ewt",
            l2=True,
            rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            rpc_uri="https://rpc.energyweb.org",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            safe_apps_rpc_uri="https://rpc.energyweb.org",
            block_explorer_uri_address_template="https://explorer.energyweb.org/address/{{address}}/transactions",
            block_explorer_uri_tx_hash_template="https://explorer.energyweb.org/tx/{{txHash}}/internal-transactions",
            block_explorer_uri_api_template="https://explorer.energyweb.org/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="Energy Web Token",
            currency_symbol="EWT",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/246/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#A566FF",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_domain_lookup.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)
        self._feature_spending_limit.chains.add(chain)


        chain = Chain.objects.create(
            name="Arbitrum 1",
            id="42161",
            description="",
            short_name="arb1",
            l2=True,
            rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            rpc_uri="https://arb1.arbitrum.io/rpc",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            safe_apps_rpc_uri="https://arb1.arbitrum.io/rpc",
            block_explorer_uri_address_template="https://arbiscan.io/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://arbiscan.io/tx/{{txHash}}",
            block_explorer_uri_api_template="https://api.arbiscan.io/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="AETH",
            currency_symbol="AETH",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/42161/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#f03c15",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0+L2",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)


        chain = Chain.objects.create(
            name="Rinkeby",
            id="4",
            description="Ethereum testnet",
            short_name="rin",
            l2=False,
            rpc_authentication=Chain.RpcAuthentication.API_KEY_PATH,
            rpc_uri="https://rinkeby.infura.io/v3/",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.API_KEY_PATH,
            safe_apps_rpc_uri="https://rinkeby.infura.io/v3/",
            block_explorer_uri_address_template="https://rinkeby.etherscan.io/address/{{address}}",
            block_explorer_uri_tx_hash_template="https://rinkeby.etherscan.io/tx/{{txHash}}",
            block_explorer_uri_api_template="https://api-rinkeby.etherscan.io/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="Ether",
            currency_symbol="ETH",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/4/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_RINKEBY_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#E8673C",
            ens_registry_address="0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e",
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_domain_lookup.chains.add(chain)
        self._feature_eip1559.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)
        self._feature_spending_limit.chains.add(chain)

        chain = Chain.objects.create(
            name="Volta",
            id="73799",
            description="",
            short_name="vt",
            l2=True,
            rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            rpc_uri="https://volta-rpc.energyweb.org",
            safe_apps_rpc_authentication=Chain.RpcAuthentication.NO_AUTHENTICATION,
            safe_apps_rpc_uri="https://volta-rpc.energyweb.org",
            block_explorer_uri_address_template="https://volta-explorer.energyweb.org/address/{{address}}/transactions",
            block_explorer_uri_tx_hash_template="https://volta-explorer.energyweb.org/tx/{{txHash}}/internal-transactions",
            block_explorer_uri_api_template="https://volta-explorer.energyweb.org/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
            currency_name="Volta Token",
            currency_symbol="VT",
            currency_decimals=18,
            currency_logo_uri="https://safe-transaction-assets.gnosis-safe.io/chains/73799/currency_logo.png",
            transaction_service_uri=TRANSACTION_SERVICE_MAINNET_URI,
            vpc_transaction_service_uri=VPC_TRANSACTION_SERVICE_MAINNET_URI,
            theme_text_color="#ffffff",
            theme_background_color="#514989",
            ens_registry_address=None,
            recommended_master_copy_version="1.3.0",
        )
        self._feature_contract_interaction.chains.add(chain)
        self._feature_domain_lookup.chains.add(chain)
        self._feature_erc721.chains.add(chain)
        self._feature_safe_apps.chains.add(chain)
        self._feature_safe_tx_gas_optional.chains.add(chain)
        self._feature_spending_limit.chains.add(chain)

        GasPrice.objects.create(
            chain_id=1,
            oracle_uri="https://ethgasstation.info/json/ethgasAPI.json",
            oracle_parameter="fast",
            gwei_factor="100000000.000000000",
            fixed_wei_value=None,
        )

        GasPrice.objects.create(
            chain_id=100,
            oracle_uri=None,
            oracle_parameter=None,
            gwei_factor="100000000.000000000",
            fixed_wei_value="1000000000",
        )

        GasPrice.objects.create(
            chain_id=137,
            oracle_uri="https://gasstation-mainnet.matic.network/",
            oracle_parameter="standard",
            gwei_factor="1000000000.000000000",
            fixed_wei_value=None,
        )

        GasPrice.objects.create(
            chain_id=56,
            oracle_uri="https://bscgas.info/gas",
            oracle_parameter="standard",
            gwei_factor="1000000000.000000000",
            fixed_wei_value=None,
        )

        GasPrice.objects.create(
            chain_id=246,
            oracle_uri="https://station.energyweb.org",
            oracle_parameter="standard",
            gwei_factor="1000000000.000000000",
            fixed_wei_value=None,
        )

        GasPrice.objects.create(
            chain_id=42161,
            oracle_uri=None,
            oracle_parameter=None,
            gwei_factor="100000000.000000000",
            fixed_wei_value="2000000000",
        )

        GasPrice.objects.create(
            chain_id=4,
            oracle_uri="https://ethgasstation.info/json/ethgasAPI.json",
            oracle_parameter="fast",
            gwei_factor="100000000.000000000",
            fixed_wei_value=None,
        )

        GasPrice.objects.create(
            chain_id=73799,
            oracle_uri="https://station.energyweb.org",
            oracle_parameter="standard",
            gwei_factor="1000000000.000000000",
            fixed_wei_value=None,
        )
