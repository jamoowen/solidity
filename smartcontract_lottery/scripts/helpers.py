from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorV2Mock,
    LinkToken,
    VRFV2Wrapper,
)


FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "wrapperAddress": VRFV2Wrapper,
    "link_token": LinkToken,
    "coordinator_address": VRFCoordinatorV2Mock
}


def get_contract(contract_name):
    """
    Contract will get contract addresses from the brownie config - if defined
    else it will deploy a mock

        args:
            contract_name(string)

        returns:
            brownie.network.contract.ProjectContract: The most recently deployed v of the contract

    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()

        contract = contract_type[-1]
        print(contract)
    else:
        contract_address = config["networks"][network.show_active(
        )][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )

    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, inital_value=INITIAL_VALUE):
    account = get_account()
    aggregator_contract = MockV3Aggregator.deploy(
        decimals, inital_value, {"from": account})
    link_contract = LinkToken.deploy({"from": account})
    coordinator_contract = VRFCoordinatorV2Mock.deploy(
        25000000000000000, 1000000000, {"from": account})
    wrapper_contract = VRFV2Wrapper.deploy(link_contract.address,
                                           aggregator_contract.address, coordinator_contract.address, {"from": account})
    wrapper_contract.setConfig(
        40000, 90000, 0, 0xff8dedfbfa60af186cf3c830acbc32c05aae823045ae5ea7da1e45fbfaba4f92, 10)


def fund_with_link(contract_address, account=None, link_token=None, amount=1000000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount,  {
                             "from": account, "gas_price": 45000000000, "gas_limit": 5000000})
    tx.wait(1)
    print("contract funded with ", amount/(10**18), "link")

    return tx
