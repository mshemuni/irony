import pytest


import numpy as np

from irony import Calibration, Fits, FitsArray


def test_calibration():
    fa = FitsArray.from_paths(["test/files/test1.fits"])
    bias = Fits.from_path("test/files/bias.fits")
    dark = Fits.from_path("test/files/dark.fits")
    flat = Fits.from_path("test/files/flat.fits")
    bdf_corrected = Fits.from_path("test/files/bdf_test.fits")

    ca = Calibration(fa)
    calibrated = ca.calibrate(zero=bias, dark=dark, flat=flat)

    np.testing.assert_equal(
        calibrated[0].data, bdf_corrected.data
    )
