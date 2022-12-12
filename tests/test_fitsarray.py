import unittest
from glob import glob
from pathlib import Path

import numpy as np

from irony import FitsArray
from irony.errors import ImageCountError


class TestFitsArray(unittest.TestCase):

    FILES = "test/test*.fit"

    def test_abs(self):
        fa = FitsArray.from_pattern(self.FILES)
        files = [str(Path(each).absolute()) for each in glob(self.FILES)]

        self.assertListEqual(abs(fa), files)

        with self.assertRaises(ImageCountError) as context:
            _ = FitsArray.from_pattern("not_available/test*.fit")

    def test_at_file(self):
        fa = FitsArray.from_pattern(self.FILES)

        with fa.at_file() as at_file:
            with open(at_file, "r") as f2r:
                self.assertListEqual(f2r.read().split(), abs(fa))

    def test_imstat(self):
        fa = FitsArray.from_pattern(self.FILES)
        stats = fa.imstat
        for i in range(len(fa)):
            self.assertDictEqual(stats.iloc[i].to_dict(), fa[i].imstat)

    def test_header(self):
        fa = FitsArray.from_pattern(self.FILES)
        header = fa.header
        for i in range(len(fa)):
            self.assertDictEqual(header.iloc[i].to_dict(), fa[i].header)

    def test_hedit(self):
        fa = FitsArray.from_pattern(self.FILES)

        header = fa.header
        for i in range(len(fa)):
            self.assertDictEqual(header.iloc[i].to_dict(), fa[i].header)

        fa.hedit("IRON", "TEST")
        header = fa.header
        for i in range(len(fa)):
            self.assertDictEqual(header.iloc[i].to_dict(), fa[i].header)

        fa.hedit("IRON", delete=True)
        header = fa.header
        for i in range(len(fa)):
            self.assertDictEqual(header.iloc[i].to_dict(), fa[i].header)

        fa.hedit("IRON", "DATE-OBS", value_is_key=True)
        header = fa.header
        for i in range(len(fa)):
            self.assertDictEqual(header.iloc[i].to_dict(), fa[i].header)

        fa.hedit("IRON", delete=True)
        header = fa.header
        for i in range(len(fa)):
            self.assertDictEqual(header.iloc[i].to_dict(), fa[i].header)

    def test_hselect(self):
        fa = FitsArray.from_pattern(self.FILES)

        hselect = fa.hselect("DATE-OBS")
        self.assertListEqual(
            hselect.to_numpy().flatten().tolist(),
            [fa[0].header["DATE-OBS"], fa[1].header["DATE-OBS"]]
            )

    def test_imarith(self):
        fa = FitsArray.from_pattern(self.FILES)

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


if __name__ == '__main__':
    unittest.main()
