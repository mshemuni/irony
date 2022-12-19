import pytest

from pathlib import Path
import numpy as np
from astropy.io import fits as afits
from astropy.stats import sigma_clipped_stats
from pandas.testing import assert_frame_equal
from photutils.detection import DAOStarFinder
from sep import Background

from src.irony import Fits

FILE = "test/files/test1.fits"


def test_abs():
    fits = Fits.from_path(FILE)
    assert abs(fits) == str(Path(FILE).absolute())


def test_doesnotexist():
    with pytest.raises(FileNotFoundError):
        _ = Fits.from_path("none_existing_path")

def test_imstat():
    fits = Fits.from_path(FILE)
    data = afits.getdata(FILE)

    assert fits.imstat == {
            'npix': data.size,
            'mean': np.round(np.mean(data), 1),
            'stddev': np.round(np.std(data), 1),
            'min': np.round(np.min(data), 1),
            'max': np.round(np.max(data), 1)
        }


def test_header():
    fits = Fits.from_path(FILE)

    h = afits.getheader(FILE)
    h_as_dict = {
        each: h[each]
        for each in h
        if each
    }

    assert fits.header == h_as_dict


def test_data():
    fits = Fits.from_path(FILE)
    np.testing.assert_equal(
        fits.data, afits.getdata(FILE)
    )


def test_background():
    fits = Fits.from_path(FILE)
    bkg = Background(afits.getdata(FILE).astype(float))

    assert isinstance(fits.background(), Background)

    np.testing.assert_equal(
        fits.background(as_array=True), bkg.back()
    )

def test_hedit():
    fits = Fits.from_path(FILE)

    h = afits.getheader(FILE)
    h_as_dict = {
        each: h[each]
        for each in h
        if each
    }

    assert fits.header == h_as_dict

    fits.hedit("IRON", "TEST")

    h = afits.getheader(FILE)
    h_as_dict = {
        each: h[each]
        for each in h
        if each
    }

    assert fits.header == h_as_dict
    assert "IRON" in fits.header

    fits.hedit("IRON", delete=True)

    h = afits.getheader(FILE)
    h_as_dict = {
        each: h[each]
        for each in h
        if each
    }

    assert fits.header == h_as_dict
    assert "IRON" not in fits.header

    fits.hedit("IRON", "DATE-OBS", value_is_key=True)

    h = afits.getheader(FILE)
    h_as_dict = {
        each: h[each]
        for each in h
        if each
    }

    assert fits.header == h_as_dict
    assert "IRON" in fits.header
    assert fits.header["IRON"] == fits.header["DATE-OBS"]

    fits.hedit("IRON", delete=True)
    assert "IRON" not in fits.header


def test_save_as():
    if Path("test/copy.fit").exists():
        Path("test/copy.fit").unlink()

    fits = Fits.from_path(FILE)
    fits.save_as("test/copy.fit")

    assert Path("test/copy.fit").exists()

    test_fits = Fits.from_path("test/copy.fit")

    np.testing.assert_equal(
        fits.data, test_fits.data
    )

    old_header = fits.header
    new_header = test_fits.header

    with pytest.raises(FileExistsError):
        fits.save_as("test/copy.fit")

    Path("test/copy.fit").unlink()


def test_imarith():
    fits = Fits.from_path(FILE)

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

    with pytest.raises(ValueError):
        _ = fits.imarith("Not supported value", "-")


def test_daofind():
    fits = Fits.from_path(FILE)
    sigma = 3
    threshold = 5
    fwhm = 3

    data = afits.getdata(FILE)
    mean, median, std = sigma_clipped_stats(data, sigma=sigma)
    daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold * std)
    sources = daofind(data - median)

    assert_frame_equal(
        sources.to_pandas(),
        fits.daofind(sigma=sigma, fwhm=fwhm, threshold=threshold)
    )

