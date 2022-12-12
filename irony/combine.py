from subprocess import PIPE

from pyraf import iraf

from .base_logger import logger
from .errors import ImageCountError
from .fits import Fits, FitsArray
from .utils import Check, Fixer


class Combine:
    def __init__(self, fits_array: FitsArray) -> None:
        """
        Constructor method
        Creates a Combine Object.

        Parameters
        ----------
        fits_array: FitsArray
            A FitsArray.
        """
        logger.info(f"Creating an instance from {self.__class__.__name__}")
        if len(fits_array) < 1:
            raise ImageCountError("There is no image to process")

        self.fits_array = fits_array
        iraf.noao(Stdout=PIPE)
        iraf.imred(Stdout=PIPE)
        iraf.ccdred(Stdout=PIPE)
        iraf.imutil(Stdout=PIPE)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id: {id(self)}, fits_array: {self.fits_array})"

    def __repr__(self) -> str:
        return self.__str__()

    def combine(self, operation: str, output: str = None, override: bool = False, reject: str = None) -> Fits:
        """
        Returns the combined Fits of FitsArray.

        Parameters
        ----------
        operation: str
            Type of operation.
        output: str, optional
            path of the new fits file.
        override: bool, optional
            Force (overwrite) the output if a file with the same name already exist.
        reject: str, optional
            Rejection method.

        Returns
        -------
        Fits
            Combined Fits of FitsArray.
        """
        logger.info(f"combine started. Parameters: {operation=}, {output=}, {override=}, {reject=}")
        Check.operation(operation)
        Check.rejection(reject)

        reject = Fixer.nonify(reject)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(output, override=override, delete=True, prefix="irony_", suffix=".fits")

        iraf.noao.imred.ccdred.combine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.combine(f"'@{at_file}'", output=output, combine=operation, reject=reject, ccdtype="")

        return Fits.from_path(output)

    def zerocombine(self, operation: str, output: str = None, override: bool = False, reject: str = None) -> Fits:
        """
        Returns the zerocombine Fits of FitsArray.

        Parameters
        ----------
        operation: str
            Type of operation.
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            Force (overwrite) the output if a file with the same name already exist.
        reject: str, optional
            Rejection method.

        Returns
        -------
        Fits
            Combined Fits of FitsArray.
        """
        logger.info(f"zerocombine started. Parameters: {operation=}, {output=}, {override=}, {reject=}")
        Check.operation(operation)
        Check.rejection(reject)

        reject = Fixer.nonify(reject)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(output, override=override, delete=True, prefix="irony_", suffix=".fits")

        iraf.noao.imred.ccdred.zerocombine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.zerocombine(f"'@{at_file}'", output=output, combine=operation, reject=reject,
                                               ccdtype="")

        return Fits.from_path(output)

    def darkcombine(self, operation: str, output: str = None, override: bool = False, reject: str = None,
                    scale: str = None) -> Fits:
        """
        Returns the darkcombine Fits of FitsArray.

        Parameters
        ----------
        operation: str
            Type of operation.
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            Force (overwrite) the output if a file with the same name already exist.
        reject: str, optional
            Rejection method.
        scale: str, optional
            Scaling method.

        Returns
        -------
        Fits
            Combined Fits of FitsArray.
        """
        logger.info(
            f"darkcombine started. Parameters: {operation=}, {output=}, {override=}, {reject=}, {scale=}"
        )
        Check.operation(operation)
        Check.rejection(reject)
        Check.scale(scale)

        reject = Fixer.nonify(reject)
        scale = Fixer.nonify(scale)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(output, override=override, delete=True, prefix="irony_", suffix=".fits")

        iraf.noao.imred.ccdred.darkcombine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.darkcombine(f"'@{at_file}'", output=output, combine=operation, reject=reject,
                                               scale=scale, ccdtype="", process="no")

        return Fits.from_path(output)

    def flatcombine(self, operation: str, output: str = None, override: bool = False, reject: str = None,
                    scale: str = None) -> Fits:
        """
        Returns the flatcombine Fits of FitsArray.

        Parameters
        ----------
        operation: str
            Type of operation.
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            Force (overwrite) the output if a file with the same name already exist.
        reject: str, optional
            Rejection method.
        scale: str, optional
            Scaling method.

        Returns
        -------
        Fits
            Combined Fits of FitsArray.
        """
        logger.info(f"flatcombine started. Parameters: {operation=}, {output=}, {override=}, {reject=}, {scale=}")
        Check.operation(operation)
        Check.rejection(reject)
        Check.scale(scale)

        reject = Fixer.nonify(reject)
        scale = Fixer.nonify(scale)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(output, override=override, delete=True, prefix="irony_", suffix=".fits")

        iraf.noao.imred.ccdred.flatcombine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.flatcombine(f"'@{at_file}'", output=output, combine=operation, reject=reject,
                                               scale=scale, ccdtype="", process="no")

        return Fits.from_path(output)

    def imsum(self, output: str = None, override: bool = False) -> Fits:
        """
        Returns the imsum Fits of FitsArray.

        Parameters
        ----------
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            Force (overwrite) the output if a file with the same name already exist.

        Returns
        -------
        Fits
            Sum of FitsArray.
        """
        logger.info(f"imsum started. Parameters:{output=}, {override=}")
        if len(self.fits_array) < 2:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(output, override=override, delete=True, prefix="irony_", suffix=".fits")

        iraf.imutil.imsum.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.imutil.imsum(f"'@{at_file}'", output=output)
        return Fits.from_path(output)
