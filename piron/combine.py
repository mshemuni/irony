import time
from subprocess import PIPE

from pyraf import iraf

from .base_logger import logger
from .errors import ImageCountError
from .fits import Fits, FitsArray
from .utils import Check, Fixer


class Combine:
    """
    fa = FitsAray('pattern')
    Combine(fa)

    Creates a Combine Object
    
    :param fits_array: A FitsArray
    :type fits_array: FitsArray
    """
    
    def __init__(self, fits_array: FitsArray) -> None:
        """Constructor method
        """
        logger.info(f"Creating an instnce from {self.__class__.__name__}")
        if len(fits_array) < 1:
            raise ImageCountError("There is no image to proccess")

        self.fits_array = fits_array
        iraf.noao(Stdout=PIPE)
        iraf.imred(Stdout=PIPE)
        iraf.ccdred(Stdout=PIPE)
        iraf.imutil(Stdout=PIPE)

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(id: {id(self)}, fits_array: {self.fits_array})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def combine(
        self,
        operation: str,
        output: str = None,
        override: bool = False,
        reject: str = None,
    ) -> Fits:
        """
        fa = FitsAray.from_pattern('pattern')
        co = Combine(fa)
        caombined = co.combine('operation_type')

        returns the combined Fits of FitsArray
        
        :param operation: Type of operation. 
        :type operation: str
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param override: force the output if a file with the same name already exist
        :type override: bool (, optional)
        
        :param reject: rejection method
        :type reject: str (, optional)

        :return: Combined Fits of FitsArray
        :rtype: Fits
        """
        logger.info(
            f"combine started. Prameters: {operation=}, {output=}, {override=}, {reject=}"
        )
        Check.operation(operation)
        Check.rejection(reject)

        reject = Fixer.nonify(reject)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(
            output,
            override=override,
            delete=True,
            prefix="piron_",
            suffix=".fits")

        iraf.noao.imred.ccdred.combine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.combine(
                f"'@{at_file}'",
                output=output,
                combine=operation,
                reject=reject,
                ccdtype="",
            )

        return Fits.from_path(output)

    def zerocombine(
        self,
        operation: str,
        output: str = None,
        override: bool = False,
        reject: str = None,
    ) -> Fits:
        """
        fa = FitsAray.from_pattern('pattern')
        co = Combine(fa)
        caombined = co.zerocombine('operation_type')

        returns the zerocombine Fits of FitsArray
        
        :param operation: Type of operation. 
        :type operation: str
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param override: force the output if a file with the same name already exist
        :type override: bool (, optional)
        
        :param reject: rejection method
        :type reject: str (, optional)

        :return: Combined Fits of FitsArray
        :rtype: Fits
        """
        logger.info(
            f"zerocombine started. Prameters: {operation=}, {output=}, {override=}, {reject=}"
        )
        Check.operation(operation)
        Check.rejection(reject)

        reject = Fixer.nonify(reject)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(
            output,
            override=override,
            delete=True,
            prefix="piron_",
            suffix=".fits")

        iraf.noao.imred.ccdred.zerocombine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.zerocombine(
                f"'@{at_file}'",
                output=output,
                combine=operation,
                reject=reject,
                ccdtype="",
            )

        return Fits.from_path(output)

    def darkcombine(
        self,
        operation: str,
        output: str = None,
        override: bool = False,
        reject: str = None,
        scale: str = None,
    ) -> Fits:
        """
        fa = FitsAray.from_pattern('pattern')
        co = Combine(fa)
        caombined = co.darkcombine('operation_type')

        returns the darkcombine Fits of FitsArray
        
        :param operation: Type of operation. 
        :type operation: str
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param override: force the output if a file with the same name already exist
        :type override: bool (, optional)
        
        :param reject: rejection method
        :type reject: str (, optional)
        
        :param scale: scaling method
        :type scale: str (, optional)

        :return: Combined Fits of FitsArray
        :rtype: Fits
        """
        logger.info(
            f"darkcombine started. Prameters: {operation=}, {output=}, {override=}, {reject=}, {scale=}"
        )
        Check.operation(operation)
        Check.rejection(reject)
        Check.scale(scale)

        reject = Fixer.nonify(reject)
        scale = Fixer.nonify(scale)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(
            output,
            override=override,
            delete=True,
            prefix="piron_",
            suffix=".fits")

        iraf.noao.imred.ccdred.darkcombine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.darkcombine(
                f"'@{at_file}'",
                output=output,
                combine=operation,
                reject=reject,
                scale=scale,
                ccdtype="",
                process="no",
            )

        return Fits.from_path(output)

    def flatcombine(
        self,
        operation: str,
        output: str = None,
        override: bool = False,
        reject: str = None,
        scale: str = None,
    ) -> Fits:
        """
        fa = FitsAray.from_pattern('pattern')
        co = Combine(fa)
        caombined = co.flatcombine('operation_type')

        returns the flatcombine Fits of FitsArray
        
        :param operation: Type of operation. 
        :type operation: str
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param override: force the output if a file with the same name already exist
        :type override: bool (, optional)
        
        :param reject: rejection method
        :type reject: str (, optional)
        
        :param scale: scaling method
        :type scale: str (, optional)

        :return: Combined Fits of FitsArray
        :rtype: Fits
        """
        logger.info(
            f"flatcombine started. Prameters: {operation=}, {output=}, {override=}, {reject=}, {scale=}"
        )
        Check.operation(operation)
        Check.rejection(reject)
        Check.scale(scale)

        reject = Fixer.nonify(reject)
        scale = Fixer.nonify(scale)

        if (not Check.is_none(reject)) and len(self.fits_array) < 3:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(
            output,
            override=override,
            delete=True,
            prefix="piron_",
            suffix=".fits")

        iraf.noao.imred.ccdred.flatcombine.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.noao.imred.ccdred.flatcombine(
                f"'@{at_file}'",
                output=output,
                combine=operation,
                reject=reject,
                scale=scale,
                ccdtype="",
                process="no",
            )

        return Fits.from_path(output)

    def imsum(self, output: str = None, override: bool = False) -> Fits:
        """
        fa = FitsAray.from_pattern('pattern')
        co = Combine(fa)
        caombined = co.imsum()

        returns the imsum Fits of FitsArray
        
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param override: force the output if a file with the same name already exist
        :type override: bool (, optional)

        :return: sum of FitsArray
        :rtype: Fits
        """
        logger.info(f"imsum started. Prameters:{output=}, {override=}")
        if len(self.fits_array) < 2:
            logger.error("Not enough image found")
            raise ImageCountError("Not enough image found")

        output = Fixer.output(
            output,
            override=override,
            delete=True,
            prefix="piron_",
            suffix=".fits")

        iraf.imutil.imsum.unlearn()
        with self.fits_array.at_file() as at_file:
            iraf.imutil.imsum(f"'@{at_file}'", output=output)
        return Fits.from_path(output)
