import pytest
from brownie import accounts


# Accounts
@pytest.fixture(scope="session")
def owner():
    yield accounts[0]


@pytest.fixture(scope="session")
def bob():
    yield accounts[1]


@pytest.fixture(scope="session")
def alice():
    yield accounts[2]


# Contracts
@pytest.fixture(scope="session")
def dAddress(DAddress, owner):
    dAddress = DAddress.deploy(
        "dAddress Book",
        "dAB",
        "https://token.daddress.org/{id}",
        0,
        {"from": owner},
    )
    yield dAddress
