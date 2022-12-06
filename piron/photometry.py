from __future__ import annotations

import math
from subprocess import PIPE
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from photutils.aperture import (CircularAnnulus, CircularAperture,
                                aperture_photometry)
from photutils.utils import calc_total_error
from pyraf import iraf
from sep import sum_circle

from .base_logger import logger
from .errors import NumberOfElemetError
from .fits import FitsArray
from .utils import Fixer


class APhot:
    """
    fa = FitsArray.from_pattern('pattern')
    APhot(fa)

    Creates an Aperture Photometry Object
    
    :param fits_array: A FitsArray
    :type fits_array: FitsArray

    """
    
    def __init__(self, fits_array: FitsArray) -> None:
        """Constructor method
        """
        logger.info("Creating an instnce from APhot")
        self.fits_array = fits_array
        self.ZMag = 25

        iraf.digiphot(Stdout=PIPE)
        iraf.digiphot.apphot(Stdout=PIPE)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(id: {id(self)}, fits_array: {self.fits_array})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def __flux2mag(
        self, flux: float, flux_error: float, exptime: float
    ) -> Tuple[float, float]:
        logger.info(
            f"Converting to mag from flux. Prameters: {flux=}, {flux_error=}, {exptime=}"
        )
        if exptime == 0:
            mag = self.ZMag + -2.5 * math.log10(flux)
        else:
            mag = self.ZMag + -2.5 * \
                math.log10(flux) + 2.5 * math.log10(exptime)
        merr = math.sqrt(flux / flux_error)
        if math.isinf(merr):
            merr = 0

        return mag, merr

    def __extract(self, keys: Union[str, list[str]]) -> pd.DataFrame:
        logger.info(f"Extracting header from FitsArray. Prameters: {keys=}")
        headers = self.fits_array.hselect(keys)
        return headers

    def photutils(
        self,
        points: pd.DataFrame,
        radius: int,
        radius_out: int = None,
        extract: Union[str, list[str]] = None,
    ) -> pd.DataFrame:
        """
        fa = FitsArray.from_pattern('pattern')
        aphot = APhot(fa)
        photomrtry = aphot.photutils(SOURCES, APERTURE)

        Does photometry of given FitsArray using `photutils` and returns a pd.DataFrame.
        
        :param points: A dataframe with `x` (`xcentroid`) and `y` (`ycentroid`) coordinates of sources for photometry
        :type points: pd.DataFrame
        
        :param fits_array: Aperture value
        :type fits_array: float

        radius_out: float, optional
            Radius for sky measurements
        
        :param radius_out: Radius for sky measurements
        :type radius_out: FitsArray (, optional)

        :param extract: Headers to be extracted from fits files during photometry
        :type extract: str o List[str] (, optional)

        :return: Phptometric result
        :rtype: pd.DataFrame
        """
        logger.info(
            f"Photutils photometry. Prameters: {points=}, {radius=}, {radius_out=}, {extract=}"
        )
        if len(points) < 1:
            logger.error("No coordinates were found")
            raise NumberOfElemetError("No coordinates were found")

        table = []
        if radius_out is None:
            aperture = CircularAperture(
                points[["xcentroid", "ycentroid"]].to_numpy().tolist(), r=radius
            )
        else:
            aperture = CircularAnnulus(
                points[["xcentroid", "ycentroid"]].to_numpy().tolist(),
                r_in=radius,
                r_out=radius_out,
            )
        for fits in self.fits_array:
            error = calc_total_error(
                fits.data, fits.background(
                    as_array=True), fits.header["EXPTIME"])
            phot_table = aperture_photometry(fits.data, aperture, error=error)
            for line in phot_table:
                table.append(
                    [
                        abs(fits),
                        line["xcenter"].value,
                        line["ycenter"].value,
                        *self.__flux2mag(
                            line["aperture_sum"],
                            line["aperture_sum_err"],
                            fits.header["EXPTIME"],
                        ),
                        line["aperture_sum"],
                        line["aperture_sum_err"],
                    ]
                )

        phot_data = pd.DataFrame(
            table,
            columns=[
                "image",
                "xcentroid",
                "ycentroid",
                "mag",
                "merr",
                "flux",
                "ferr"],
        ).set_index("image")

        phot_data = phot_data.astype(float)

        if extract is not None:
            extracted_headers = self.__extract(extract)
            if len(extracted_headers) != 0:
                return pd.merge(
                    phot_data,
                    extracted_headers,
                    left_index=True,
                    right_index=True)

        return phot_data

    def sep(
        self, points: pd.DataFrame, radius: int, extract: list[str] = None
    ) -> pd.DataFrame:
        """
        fa = FitsArray.from_pattern('pattern')
        aphot = APhot(fa)
        photomrtry = aphot.sep(SOURCES, APERTURE)

        Does photometry of given FitsArray using `sep` and returns a pd.DataFrame.
        
        :param points: A dataframe with `x` (`xcentroid`) and `y` (`ycentroid`) coordinates of sources for photometry
        :type points: pd.DataFrame

        radius: float
            Aperture value
        
        :param radius: Aperture value
        :type radius: float
        
        :param extract: Headers to be extracted from fits files during photometry
        :type extract: str o List[str] (, optional)

        :return: Phptometric result
        :rtype: pd.DataFrame
        """
        logger.info(
            f"sep photometry. Prameters: {points=}, {radius=}, {extract=}")
        if len(points) < 1:
            logger.error("No coordinates were found")
            raise NumberOfElemetError("No coordinates were found")

        table = []
        for fits in self.fits_array:
            fluxes, ferrs, flag = sum_circle(
                fits.data, points["xcentroid"], points["xcentroid"], radius
            )
            for x, y, flux, ferr in zip(
                points["xcentroid"], points["xcentroid"], fluxes, ferrs
            ):
                table.append(
                    [
                        abs(fits),
                        x,
                        y,
                        *self.__flux2mag(flux, ferr, fits.header["EXPTIME"]),
                        flux,
                        ferr,
                    ]
                )

        phot_data = pd.DataFrame(
            table,
            columns=[
                "image",
                "xcentroid",
                "ycentroid",
                "mag",
                "merr",
                "flux",
                "ferr"],
        ).set_index("image")

        phot_data = phot_data.astype(float)

        if extract is not None:
            extracted_headers = self.__extract(extract)
            if len(extracted_headers) != 0:
                return pd.merge(
                    phot_data,
                    extracted_headers,
                    left_index=True,
                    right_index=True)

        return phot_data

    def iraf(
        self,
        points: pd.DataFrame,
        aperture: float,
        annulus: float,
        dannulu: float,
        extract: list[str] = None,
    ) -> pd.DataFrame:
        """
        fa = FitsArray.from_pattern('pattern')
        aphot = APhot(fa)
        photomrtry = aphot.iraf(SOURCES, APERTURE)

        Does photometry of given FitsArray using `iraf` and returns a pd.DataFrame.
        
        :param points: A dataframe with `x` (`xcentroid`) and `y` (`ycentroid`) coordinates of sources for photometry
        :type points: pd.DataFrame
        
        :param aperture: Aperture value
        :type aperture: float
        
        :param annulus: Annulus for sky measurements
        :type annulus: float (, optional)
        
        :param dannulus: Dannulus for sky measurements
        :type dannulus: float (, optional)
        
        :param extract: Headers to be extracted from fits files during photometry
        :type extract: str o List[str] (, optional)

        :return: Phptometric result
        :rtype: pd.DataFrame
        """
        logger.info("iraf photometry")
        if len(points) < 1:
            logger.error("No coordinates were found")
            raise NumberOfElemetError("No coordinates were found")

        iraf.digiphot.apphot.datapars.unlearn()
        iraf.digiphot.apphot.centerpars.unlearn()
        iraf.digiphot.apphot.fitskypars.unlearn()
        iraf.digiphot.apphot.photpars.unlearn()
        iraf.digiphot.apphot.phot.unlearn()

        iraf.digiphot.apphot.datapars.gain = ""

        iraf.digiphot.apphot.centerpars.cbox = aperture / 2

        iraf.digiphot.apphot.fitskypars.salgori = "centroid"
        iraf.digiphot.apphot.fitskypars.annulus = annulus
        iraf.digiphot.apphot.fitskypars.dannulu = dannulu

        iraf.digiphot.apphot.photpars.weighting = "constant"
        iraf.digiphot.apphot.photpars.aperture = aperture
        iraf.digiphot.apphot.photpars.zmag = self.ZMag
        iraf.digiphot.apphot.photpars.mkapert = "no"
        with self.fits_array.at_file() as at_file:
            with Fixer.to_new_directory(None, self.fits_array) as output_files:
                with Fixer.at_file_from_list(
                    " ".join(map(str, each))
                    for each in points[["xcentroid", "ycentroid"]].to_numpy()
                ) as coo_file:

                    iraf.digiphot.apphot.phot(
                        f"'@{at_file}'",
                        coords=f"{coo_file}",
                        output=f"'@{output_files}'",
                        interac="no",
                        verify="no",
                    )
                    res = iraf.txdump(
                        f"'@{output_files}'",
                        "id,mag,merr,flux,stdev",
                        "yes",
                        Stdout=PIPE,
                    )
                    res = pd.DataFrame(
                        [each.split() for each in res],
                        columns=["id", "mag", "merr", "flux", "stdev"],
                    )

                    result = []

                    for each in res.groupby("id"):
                        coords = points.iloc[int(each[0]) - 1][
                            ["xcentroid", "ycentroid"]
                        ].tolist()
                        for i, path in zip(
                                range(len(each[1])), abs(self.fits_array)):
                            phot = each[1].iloc[i]
                            result.append(
                                [
                                    path,
                                    coords[0],
                                    coords[1],
                                    phot.mag,
                                    phot.merr,
                                    phot.flux,
                                    phot.stdev,
                                ]
                            )

                    phot_data = pd.DataFrame(
                        result,
                        columns=[
                            "image",
                            "xcentroid",
                            "ycentroid",
                            "mag",
                            "merr",
                            "flux",
                            "ferr",
                        ],
                    ).set_index("image")

                    phot_data = phot_data.astype(float)

                    if extract is not None:
                        extracted_headers = self.__extract(extract)
                        if len(extracted_headers) != 0:
                            return pd.merge(
                                phot_data,
                                extracted_headers,
                                left_index=True,
                                right_index=True,
                            )

                    return phot_data
