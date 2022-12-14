import pytest

from glob import glob
from pathlib import Path

import numpy as np

from irony import FitsArray
from irony.errors import ImageCountError

FILES = "test/files/test*.fits"


def test_abs():
    fa = FitsArray.from_pattern(FILES)
    files = [str(Path(each).absolute()) for each in glob(FILES)]

    assert abs(fa) == files

    with pytest.raises(ImageCountError):
        _ = FitsArray.from_pattern("not_available/test*.fit")


def test_at_file():
    fa = FitsArray.from_pattern(FILES)

    with fa.at_file() as at_file:
        with open(at_file, "r") as f2r:
            assert f2r.read().split() == abs(fa)


def test_imstat():
    fa = FitsArray.from_pattern(FILES)
    stats = fa.imstat
    for i in range(len(fa)):
        assert stats.iloc[i].to_dict() == fa[i].imstat


def test_header():
    fa = FitsArray.from_pattern(FILES)
    header = fa.header
    for i in range(len(fa)):
        assert header.iloc[i].to_dict() == fa[i].header

def test_hedit():
    fa = FitsArray.from_pattern(FILES)

    header = fa.header
    for i in range(len(fa)):
        assert header.iloc[i].to_dict() == fa[i].header

    fa.hedit("IRON", "TEST")
    header = fa.header
    for i in range(len(fa)):
        assert header.iloc[i].to_dict() == fa[i].header

    fa.hedit("IRON", delete=True)
    header = fa.header
    for i in range(len(fa)):
        assert header.iloc[i].to_dict() == fa[i].header

    fa.hedit("IRON", "DATE-OBS", value_is_key=True)
    header = fa.header
    for i in range(len(fa)):
        assert header.iloc[i].to_dict() == fa[i].header

    fa.hedit("IRON", delete=True)
    header = fa.header
    for i in range(len(fa)):
        assert header.iloc[i].to_dict() == fa[i].header


def test_hselect():
    fa = FitsArray.from_pattern(FILES)

    hselect = fa.hselect("DATE-OBS")
    assert hselect.to_numpy().flatten().tolist() == [fa[0].header["DATE-OBS"], fa[1].header["DATE-OBS"]]


def test_imarith():
    fa = FitsArray.from_pattern(FILES)

    new_fa = fa.imarith(10, "*")

    np.testing.assert_equal(
        new_fa[0].data, fa[0].data * 10
    )

    np.testing.assert_equal(
        new_fa[1].data, fa[1].data * 10
    )

    new_fa = fa.imarith(2, "/")
    np.testing.assert_equal(
        new_fa[0].data, fa[0].data / 2
    )

    np.testing.assert_equal(
        new_fa[1].data, fa[1].data / 2
    )

    new_fa = fa.imarith(fa, "+")
    np.testing.assert_equal(
        new_fa[0].data, fa[0].data * 2
    )

    np.testing.assert_equal(
        new_fa[1].data, fa[1].data * 2
    )

    new_fa = fa.imarith(fa, "-")
    np.testing.assert_equal(
        new_fa[0].data, fa[0].data * 0
    )

    np.testing.assert_equal(
        new_fa[1].data, fa[1].data * 0
    )

    new_fa = fa.imarith(fa[0], "-")
    np.testing.assert_equal(
        new_fa[0].data, fa[0].data * 0
    )

    np.testing.assert_equal(
        new_fa[1].data, fa[1].data - fa[0].data
    )

    new_fa = fa.imarith([2, 3], "*")
    np.testing.assert_equal(
        new_fa[0].data, fa[0].data * 2
    )

    np.testing.assert_equal(
        new_fa[1].data, fa[1].data * 3
    )