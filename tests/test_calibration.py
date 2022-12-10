import unittest

import numpy as np

from irony import Calibration, Fits, FitsArray


class TestCalibration(unittest.TestCase):

    def test_calibration(self):
        fa = FitsArray.from_paths(["test/test.fit"])
        bias = Fits.from_path("test/bias.fit")
        dark = Fits.from_path("test/dark.fit")
        flat = Fits.from_path("test/flat.fit")
        bdf_corrected = Fits.from_path("test/bdf_test.fit")

        ca = Calibration(fa)
        calibrated = ca.calibrate(zero=bias, dark=dark, flat=flat)

        np.testing.assert_equal(
            calibrated[0].data, bdf_corrected.data
        )


if __name__ == '__main__':
    unittest.main()
