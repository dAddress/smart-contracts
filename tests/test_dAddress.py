from brownie import ZERO_ADDRESS
import brownie
import pytest

bookName = "Book 1"


def test_mint_address_book(dAddress, bob):
    assert dAddress.balanceOf(bob) == 0
    assert dAddress.totalSupply() == 0

    tx = dAddress.mint(bob, bookName, {"from": bob})
    tokenId = tx.return_value

    assert tokenId == dAddress.totalSupply()
    assert tokenId == 1

    assert tx.events.count("Transfer") == 1
    log = tx.events["Transfer"][0]
    log["sender"] == ZERO_ADDRESS
    log["receiver"] == bob
    log["tokenId"] == 1

    assert tx.events.count("BookCreation") == 1
    log = tx.events["BookCreation"][0]
    assert log["owner"] == bob
    assert log["bookName"] == bookName

    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    assert dAddress.bookName(1) == bookName
    assert dAddress.bookId(bookName) == 1


def test_set_address(dAddress, bob):
    dAddress.mint(bob, bookName, {"from": bob})
    dAddress.setAddress("Book 1", "Bob", bob, {"from": bob})

    assert dAddress.dAddressOf("Book 1", "Bob") == bob


def test_set_valid_address(dAddress, validator, bob):
    addressName = "Contract Name"

    validator.setAddressInfo(bookName, addressName, {"from": bob})

    dAddress.mint(bob, bookName, {"from": bob})
    dAddress.setAddress(bookName, addressName, validator, True, {"from": bob})

    assert dAddress.dAddressOf(bookName, addressName) == validator
    assert dAddress.validateContract(bookName, addressName)

    validator.setAddressInfo(bookName, "something else", {"from": bob})
    with brownie.reverts("Not valid"):
        dAddress.validateContract(bookName, addressName)

    dAddress.setAddress(bookName, addressName, bob, True, {"from": bob})
    with brownie.reverts("Not a contract"):
        dAddress.validateContract(bookName, addressName)


def test_transfer(dAddress, bob, alice):
    dAddress.mint(bob, bookName, {"from": bob})
    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    dAddress.mint(alice, "Book 2", {"from": bob})
    assert dAddress.balanceOf(alice) == 1
    assert dAddress.ownerOf(2) == alice
    assert dAddress.tokenOfOwnerByIndex(alice, 0) == 2

    dAddress.transferFrom(bob, alice, 1, {"from": bob})
    assert dAddress.balanceOf(bob) == 0
    with brownie.reverts():
        dAddress.tokenOfOwnerByIndex(bob, 0)
    assert dAddress.ownerOf(1) == alice
    assert dAddress.balanceOf(alice) == 2
    assert dAddress.tokenOfOwnerByIndex(alice, 0) == 2
    assert dAddress.tokenOfOwnerByIndex(alice, 1) == 1


def test_safe_transfer(dAddress, receiver, bob):
    dAddress.mint(bob, bookName, {"from": bob})
    assert dAddress.balanceOf(bob) == 1
    assert dAddress.ownerOf(1) == bob
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1

    receiver.setTokenOwner(dAddress, 1, {"from": bob})
    dAddress.safeTransferFrom(bob, receiver, 1, {"from": bob})
    assert dAddress.balanceOf(bob) == 0
    with brownie.reverts():
        dAddress.tokenOfOwnerByIndex(bob, 0)
    assert dAddress.ownerOf(1) == receiver
    assert dAddress.balanceOf(receiver) == 1
    assert dAddress.tokenOfOwnerByIndex(receiver, 0) == 1
    

    receiver.returnToken(dAddress, 1, {"from": bob})
    assert dAddress.balanceOf(bob) == 1
    with brownie.reverts():
        dAddress.tokenOfOwnerByIndex(receiver, 0)
    assert dAddress.ownerOf(1) == bob
    assert dAddress.balanceOf(receiver) == 0
    assert dAddress.tokenOfOwnerByIndex(bob, 0) == 1