from brownie import ZERO_ADDRESS, convert
import pytest
import codecs


def test_mint_address_book(dAddress, bob):
    bookName = "Book 1"

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
