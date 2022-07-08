import pytest
from brownie import accounts


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


# Accounts
@pytest.fixture
def owner():
    yield accounts[0]


@pytest.fixture
def bob():
    yield accounts[1]


@pytest.fixture
def alice():
    yield accounts[2]


# Contracts
@pytest.fixture
def dAddress(DAddress, owner):
    dAddress = DAddress.deploy(
        "dAddress Book",
        "dAB",
        "https://token.daddress.org/{id}",
        0,
        {"from": owner},
    )

    yield dAddress


@pytest.fixture
def validator(Validator, owner):
    validator = Validator.deploy({"from": owner})

    yield validator


@pytest.fixture
def receiver(NFTReceiver, owner):
    receiver = NFTReceiver.deploy({"from": owner})

    yield receiver
