from subprocess import PIPE

from pyraf import iraf

from .base_logger import logger
from .errors import ImageCountError, NothingToDoError
from .fits import Fits, FitsArray
from .utils import Fixer


class Calibration:
    def __init__(self, fits_array: FitsArray) -> None:
        """
        Constructor method.
        Creates a Calibration Object.

        Parameters
        ----------
        fits_array: FitsArray
            A FitsArray.
        """
        logger.info(f"Creating an instance from {self.__class__.__name__}")
        if len(fits_array) < 1:
            logger.error("There is no image to process")
            raise ImageCountError("There is no image to process")

        self.fits_array = fits_array
        iraf.noao(Stdout=PIPE)
        iraf.imred(Stdout=PIPE)
        iraf.ccdred(Stdout=PIPE)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(@: {id(self)}, data: {self.fits_array})"

    def __repr__(self) -> str:
        return self.__str__()

    def calibrate(self, zero: Fits = None, dark: Fits = None, flat: Fits = None, output: str = None) -> FitsArray:
        """
        Returns the calibrated FitsArray.

        Parameters
        ----------
        zero: Fits
            Fits object of master zero. If None, zero correction will be skipped.
        dark: Fits
            Fits object of master dark. If None, dark correction will be skipped.
        flat: Fits
            Fits object of master flat. If None, flat correction will be skipped.
        output: str, optional
            Path of the new fits file.

        Returns
        -------
        FitsArray
            Calibrated FitsArray.
        """
        logger.info(f"Calibration started. Parameters: {output=}, {zero=}, {dark=}, {flat=}")
        if all([v is None for v in [zero, dark, flat]]):
            logger.error("Nothing neither of zero, dark ot flat ise provided. Nothing to do.")
            raise NothingToDoError("Nothing neither of zero, dark ot flat ise provided. Nothing to do.")

        zero_path = "" if zero is None else abs(zero)
        dark_path = "" if dark is None else abs(dark)
        flat_path = "" if flat is None else abs(flat)

        with self.fits_array.at_file() as at_file:
            with Fixer.to_new_directory(output, self.fits_array) as new_files:
                iraf.noao.imred.ccdred.ccdproc.unlearn()

                iraf.noao.imred.ccdred.ccdproc(f"'@{at_file}'", output=f"'@{new_files}'", noproc="no", ccdtype="",
                                               fixpix="no", oversca="no", trim="no",
                                               zerocor=Fixer.yesnoify(zero is not None), zero=zero_path,
                                               darkcor=Fixer.yesnoify(dark is not None), dark=dark_path,
                                               flatcor=Fixer.yesnoify(flat is not None), flat=flat_path)
                with open(new_files, "r") as to_save:
                    return FitsArray.from_paths(to_save.read().split())
