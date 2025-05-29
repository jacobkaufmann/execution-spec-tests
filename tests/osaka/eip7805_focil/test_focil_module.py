"""
abstract: Tests [EIP-7805 focil](https://eips.ethereum.org/EIPS/eip-7805)
    Test cases for [EIP-7805 focil](https://eips.ethereum.org/EIPS/eip-7805)].
"""

import pytest

from ethereum_test_base_types import Bytes
from ethereum_test_tools import Account, Alloc, Block, BlockException, BlockchainTestFiller, Transaction
from ethereum_test_tools.vm.opcode import Opcodes as Op
from ethereum_test_types import Environment

REFERENCE_SPEC_GIT_PATH = "DUMMY/eip-DUMMY.md"
REFERENCE_SPEC_VERSION = "DUMMY_VERSION"


@pytest.mark.valid_from("Osaka")
@pytest.mark.blockchain_test_engine_only
def test_focil_module_nonempty_payload_empty_il(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    A non-empty execution payload and an empty inclusion list.
    """

    sender = pre.fund_eoa(100_000_000_000)
    recipient = pre.fund_eoa()

    value = 100

    tx = Transaction(
        ty=0x01,
        to=recipient,
        gas_limit=21000,
        data=b"",
        value=value,
        sender=sender,
    )
    tx.sign()

    post = {}

    block = Block(txs=[tx], inclusion_list=[])

    blockchain_test(pre=pre, blocks=[block], post=post)


@pytest.mark.valid_from("Osaka")
@pytest.mark.blockchain_test_engine_only
def test_focil_module_nonempty_payload_nonempty_il(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    A non-empty execution payload with a single transaction and a non-empty inclusion list that contains only that single transaction.
    """

    sender = pre.fund_eoa(100_000_000_000)
    recipient = pre.fund_eoa()

    value = 100

    tx = Transaction(
        ty=0x01,
        to=recipient,
        gas_limit=21000,
        data=b"",
        value=value,
        sender=sender,
    )
    tx.sign()

    post = {}

    block = Block(txs=[tx], inclusion_list=[tx.rlp()])

    blockchain_test(pre=pre, blocks=[block], post=post)


@pytest.mark.valid_from("Osaka")
@pytest.mark.blockchain_test_engine_only
def test_focil_module_empty_payload_nonempty_il_invalid_tx_invalid_encoding(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    An empty execution payload and a non-empty inclusion list that contains a single transaction that is an invalid encoding.
    """

    sender = pre.fund_eoa(100_000_000_000)
    recipient = pre.fund_eoa()

    value = 100

    tx = Transaction(
        ty=0x01,
        to=recipient,
        gas_limit=21000,
        data=b"",
        value=value,
        sender=sender,
    )
    tx.sign()

    rlp = tx.rlp().hex()

    post = {}

    block = Block(txs=[], inclusion_list=[Bytes("0xFF" + rlp[2:])])

    blockchain_test(pre=pre, blocks=[block], post=post)


@pytest.mark.valid_from("Osaka")
@pytest.mark.blockchain_test_engine_only
def test_focil_module_empty_payload_nonempty_il_invalid_tx_insufficient_gas_limit(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    An empty execution payload and a non-empty inclusion list that contains a single transaction that could consume more gas than what is available.
    """

    block = Block(txs=[])

    block_gas_limit = Environment().gas_limit

    sender = pre.fund_eoa(100_000_000_000)
    recipient = pre.fund_eoa()

    value = 100

    tx = Transaction(
        ty=0x01,
        to=recipient,
        gas_limit=block_gas_limit + 1,
        data=b"",
        value=value,
        sender=sender,
    )
    tx.sign()

    block.inclusion_list = [tx.rlp()]

    post = {}

    blockchain_test(pre=pre, blocks=[block], post=post)


@pytest.mark.valid_from("Osaka")
@pytest.mark.blockchain_test_engine_only
def test_focil_module_empty_payload_nonempty_il_invalid_tx_insufficient_balance(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    An empty execution payload and a non-empty inclusion list that contains a single transaction that transfers more ETH than what is available.
    """

    value = 1000

    sender = pre.fund_eoa(value - 1)
    recipient = pre.fund_eoa()


    tx = Transaction(
        ty=0x01,
        to=recipient,
        gas_limit=21000,
        data=b"",
        value=value,
        sender=sender,
    )
    tx.sign()

    post = {}

    block = Block(txs=[], inclusion_list=[tx.rlp()])

    blockchain_test(pre=pre, blocks=[block], post=post)


@pytest.mark.valid_from("Osaka")
@pytest.mark.blockchain_test_engine_only
@pytest.mark.exception_test
def test_focil_module_empty_payload_nonempty_il_valid_tx(blockchain_test: BlockchainTestFiller, pre: Alloc):
    """
    An empty execution payload and a non-empty valid inclusion list that contains a single valid transaction, which should have been included.
    """

    sender = pre.fund_eoa(100_000_000_000)
    recipient = pre.fund_eoa()

    value = 100

    tx = Transaction(
        ty=0x01,
        to=recipient,
        gas_limit=21000,
        data=b"",
        value=value,
        sender=sender,
    )
    tx.sign()

    post = {}

    block = Block(txs=[], inclusion_list=[tx.rlp()])
    block.exception = BlockException.UNSATISFIED_INCLUSION_LIST

    blockchain_test(pre=pre, blocks=[block], post=post)
