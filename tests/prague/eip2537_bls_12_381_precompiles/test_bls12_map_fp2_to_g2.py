"""
abstract: Tests BLS12_MAP_FP2_TO_G2 precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537)
    Tests BLS12_MAP_FP2_TO_G2 precompile of [EIP-2537: Precompile for BLS12-381 curve operations](https://eips.ethereum.org/EIPS/eip-2537).
"""  # noqa: E501

import pytest

from ethereum_test_tools import Alloc, Environment, StateTestFiller, Transaction
from ethereum_test_tools import Opcodes as Op

from .conftest import G2_FIELD_POINTS_MAP_TO_IDENTITY
from .helpers import vectors_from_file
from .spec import FP2, PointG2, Spec, ref_spec_2537

REFERENCE_SPEC_GIT_PATH = ref_spec_2537.git_path
REFERENCE_SPEC_VERSION = ref_spec_2537.version

pytestmark = [
    pytest.mark.valid_from("Prague"),
    pytest.mark.parametrize("precompile_address", [Spec.MAP_FP2_TO_G2], ids=[""]),
]

G2_POINT_ZERO_FP = PointG2(
    (
        0x18320896EC9EEF9D5E619848DC29CE266F413D02DD31D9B9D44EC0C79CD61F18B075DDBA6D7BD20B7FF27A4B324BFCE,  # noqa: E501
        0xA67D12118B5A35BB02D2E86B3EBFA7E23410DB93DE39FB06D7025FA95E96FFA428A7A27C3AE4DD4B40BD251AC658892,  # noqa: E501
    ),
    (
        0x260E03644D1A2C321256B3246BAD2B895CAD13890CBE6F85DF55106A0D334604FB143C7A042D878006271865BC35941,  # noqa: E501
        0x4C69777A43F0BDA07679D5805E63F18CF4E0E7C6112AC7F70266D199B4F76AE27C6269A3CEEBDAE30806E9A76AADF5C,  # noqa: E501
    ),
)


@pytest.mark.parametrize(
    "input_data,expected_output,vector_gas_value",
    # Test vectors from the reference spec (from the cryptography team)
    vectors_from_file("map_fp2_to_G2_bls.json")
    + [
        pytest.param(
            FP2((0, 0)),
            G2_POINT_ZERO_FP,
            None,
            id="fp_0",
        ),
        pytest.param(
            FP2((Spec.P - 1, Spec.P - 1)),
            PointG2(
                (
                    0x9BF1B857D8C15F317F649ACCFA7023EF21CFC03059936B83B487DB476FF9D2FE64C6147140A5F0A436B875F51FFDF07,  # noqa: E501
                    0xBB10E09BDF236CB2951BD7BCC044E1B9A6BB5FD4B2019DCC20FFDE851D52D4F0D1A32382AF9D7DA2C5BA27E0F1C69E6,  # noqa: E501
                ),
                (
                    0xDD416A927AB1C15490AB753C973FD377387B12EFCBE6BED2BF768B9DC95A0CA04D1A8F0F30DBC078A2350A1F823CFD3,  # noqa: E501
                    0x171565CE4FCD047B35EA6BCEE4EF6FDBFEC8CC73B7ACDB3A1EC97A776E13ACDFEFFC21ED6648E3F0EEC53DDB6C20FB61,  # noqa: E501
                ),
            ),
            None,
            id="fp_p_minus_1",
        ),
        pytest.param(
            FP2(
                (
                    3510328712861478240121438855244276237335901234329585006107499559909114695366216070652508985150831181717984778988906,  # noqa: E501
                    2924545590598115509050131525615277284817672420174395176262156166974132393611647670391999011900253695923948997972401,  # noqa: E501
                )
            ),
            Spec.INF_G2,
            None,
            id="fp_map_to_inf",
        ),
    ],
)
def test_valid(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_MAP_FP2_TO_G2 precompile."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize("expected_output", [Spec.INF_G2], ids=[""])
@pytest.mark.parametrize(
    "input_data,vector_gas_value",
    [
        pytest.param(t, None, id=f"isogeny_kernel_{i}")
        for i, t in enumerate(G2_FIELD_POINTS_MAP_TO_IDENTITY)
    ],
)
def test_isogeny_kernel_values(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """
    Test the BLS12_MAP_FP2_TO_G2 precompile with isogeny kernel values. Note this test only exists
    to align with the G1 test. `G2_FIELD_POINTS_MAP_TO_IDENTITY` is empty so there are no cases.

    The isogeny kernel is simply the set of special field values, that after the two step mapping
    (first SWU onto an auxiliary curve, then a 3-degree isogeny back to G2), collapse exactly
    to the identity point.

    For the G2 case the only kernel element is the point at infinity, and SWU never produces the
    identity point from a finite input t. Hence `G2_FIELD_POINTS_MAP_TO_IDENTITY` is empty. Please
    proceed to the generator in `helpers.py` for more details.
    """
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input_data",
    # Test vectors from the reference spec (from the cryptography team)
    vectors_from_file("fail-map_fp2_to_G2_bls.json")
    + [
        pytest.param(b"\x80" + bytes(FP2((0, 0)))[1:], id="invalid_encoding"),
        pytest.param(bytes(FP2((0, 0)))[1:], id="input_too_short"),
        pytest.param(b"\x00" + FP2((0, 0)), id="input_too_long"),
        pytest.param(b"", id="zero_length_input"),
        pytest.param(FP2((Spec.P, 0)), id="fq_eq_q"),
        pytest.param(FP2((0, Spec.P)), id="fq_eq_q_2"),
        pytest.param(FP2((2**512 - 1, 0)), id="fq_eq_2_512_minus_1"),
        pytest.param(FP2((0, 2**512 - 1)), id="fq_eq_2_512_minus_1_2"),
        pytest.param(Spec.G2, id="g2_input"),
        pytest.param(FP2((Spec.P + 1, 0)), id="fp2_above_modulus_c0"),
        pytest.param(FP2((0, Spec.P + 1)), id="fp2_above_modulus_c1"),
        pytest.param(FP2((2**384, 0)), id="fp2_large_power_of_2_c0"),
        pytest.param(FP2((0, 2**384)), id="fp2_large_power_of_2_c1"),
        pytest.param(bytes(FP2((0, 0))) + bytes([0x00]), id="fp2_with_extra_byte"),
        pytest.param(bytes(FP2((0, 0)))[:95], id="fp2_one_byte_short"),
        pytest.param(bytes([0xFF]) + bytes(FP2((0, 0)))[1:], id="fp2_invalid_first_byte"),
        pytest.param(Spec.INF_G2, id="g2_inf_input"),
    ],
)
@pytest.mark.parametrize("expected_output", [Spec.INVALID], ids=[""])
def test_invalid(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Negative tests for the BLS12_MAP_FP_TO_G2 precompile."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "input_data,expected_output,precompile_gas_modifier",
    [
        pytest.param(
            FP2((0, 0)),
            G2_POINT_ZERO_FP,
            1,
            id="extra_gas",
        ),
        pytest.param(
            FP2((0, 0)),
            Spec.INVALID,
            -1,
            id="insufficient_gas",
        ),
    ],
)
def test_gas(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_MAP_FP_TO_G2 precompile gas requirements."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )


@pytest.mark.parametrize(
    "call_opcode",  # Note `Op.CALL` is used for all the `test_valid` cases.
    [
        Op.STATICCALL,
        Op.DELEGATECALL,
        Op.CALLCODE,
    ],
)
@pytest.mark.parametrize(
    "input_data,expected_output",
    [
        pytest.param(
            FP2((0, 0)),
            G2_POINT_ZERO_FP,
            id="fp_0",
        ),
    ],
)
def test_call_types(
    state_test: StateTestFiller,
    pre: Alloc,
    post: dict,
    tx: Transaction,
):
    """Test the BLS12_MAP_FP_TO_G2 precompile using different call types."""
    state_test(
        env=Environment(),
        pre=pre,
        tx=tx,
        post=post,
    )
