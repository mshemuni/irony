import unittest
from pathlib import Path

import numpy as np
from astropy.io import fits as afits
from astropy.stats import sigma_clipped_stats
from pandas.testing import assert_frame_equal
from photutils.detection import DAOStarFinder
from sep import Background

from piron import Fits


class TestFits(unittest.TestCase):

    def test_abs(self):
        fits = Fits.from_path("test/test.fit")
        self.assertEqual(abs(fits), str(Path("test/test.fit").absolute()))

    def test_doesnotexist(self):
        with self.assertRaises(FileNotFoundError) as context:
            _ = Fits.from_path("none_existing_path")

    def test_imstat(self):
        fits = Fits.from_path("test/test.fit")
        self.assertDictEqual(
            fits.imstat, {
                'npix': 4194304.0, 'mean': 1110.0, 'stddev': 5.209,
                'min': 1080.0, 'max': 1259.0
            }
        )

    def test_header(self):
        fits = Fits.from_path("test/test.fit")

        h = afits.getheader("test/test.fit")
        h_as_dict = {
            each: h[each]
            for each in h
            if each
        }

        self.assertDictEqual(fits.header, h_as_dict)

    def test_data(self):
        fits = Fits.from_path("test/test.fit")
        np.testing.assert_equal(
            fits.data, afits.getdata("test/test.fit")
        )

    def test_background(self):
        fits = Fits.from_path("test/test.fit")
        bkg = Background(afits.getdata("test/test.fit").astype(float))
        self.assertIsInstance(
            fits.background(), Background
        )

        np.testing.assert_equal(
            fits.background(as_array=True), bkg.back()
        )

    def test_hedit(self):
        fits = Fits.from_path("test/test.fit")

        h = afits.getheader("test/test.fit")
        h_as_dict = {
            each: h[each]
            for each in h
            if each
        }

        self.assertDictEqual(fits.header, h_as_dict)

        fits.hedit("IRON", "TEST")

        h = afits.getheader("test/test.fit")
        h_as_dict = {
            each: h[each]
            for each in h
            if each
        }

        self.assertDictEqual(fits.header, h_as_dict)
        self.assertIn("IRON", fits.header)

        fits.hedit("IRON", delete=True)

        h = afits.getheader("test/test.fit")
        h_as_dict = {
            each: h[each]
            for each in h
            if each
        }

        self.assertDictEqual(fits.header, h_as_dict)
        self.assertNotIn("IRON", fits.header)

        fits.hedit("IRON", "DATE-OBS", value_is_key=True)

        h = afits.getheader("test/test.fit")
        h_as_dict = {
            each: h[each]
            for each in h
            if each
        }

        self.assertDictEqual(fits.header, h_as_dict)

        self.assertIn("IRON", fits.header)
        self.assertEqual(fits.header["IRON"], fits.header["DATE-OBS"])
        fits.hedit("IRON", delete=True)
        self.assertNotIn("IRON", fits.header)

    def test_save_as(self):
        if Path("test/copy.fit").exists():
            Path("test/copy.fit").unlink()

        fits = Fits.from_path("test/test.fit")
        fits.save_as("test/copy.fit")

        self.assertTrue(Path("test/copy.fit").exists())

        test_fits = Fits.from_path("test/copy.fit")

        np.testing.assert_equal(
            fits.data, test_fits.data
        )

        old_header = fits.header
        new_header = test_fits.header
        del old_header["IRAF-TLM"]
        del new_header["IRAF-TLM"]
        del old_header["DATE"]
        del new_header["DATE"]
        self.assertDictEqual(old_header, new_header)

        with self.assertRaises(FileExistsError) as context:
            fits.save_as("test/copy.fit")

        Path("test/copy.fit").unlink()

    def test_imarith(self):
        fits = Fits.from_path("test/test.fit")

        new_fits = fits.imarith(10, "*")
        np.testing.assert_equal(
            new_fits.data, fits.data * 10
        )

        new_fits = fits.imarith(2, "/")
        np.testing.assert_equal(
            new_fits.data, fits.data / 2
        )

        new_fits = fits.imarith(fits, "+")
        np.testing.assert_equal(
            new_fits.data, fits.data * 2
        )

        new_fits = fits.imarith(fits, "-")
        np.testing.assert_equal(
            new_fits.data, fits.data * 0
        )

        with self.assertRaises(ValueError) as context:
            _ = fits.imarith("Not supported value", "-")

    def test_daofind(self):
        fits = Fits.from_path("test/test.fit")
        sigma = 3
        threshold = 5
        fwhm = 3

        data = afits.getdata("test/test.fit")
        mean, median, std = sigma_clipped_stats(data, sigma=sigma)
        daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold * std)
        sources = daofind(data - median)

        assert_frame_equal(
            sources.to_pandas(),
            fits.daofind(sigma=sigma, fwhm=fwhm, threshold=threshold)
            )


if __name__ == '__main__':
    unittest.main()
