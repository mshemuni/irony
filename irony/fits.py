from __future__ import annotations

import contextlib
import subprocess
import tempfile
from glob import glob
from pathlib import Path
from subprocess import PIPE
from typing import Dict, List, Union, Hashable

import astroalign
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from astropy.io import fits as fts
from astropy.stats import sigma_clipped_stats
from astropy.visualization import ZScaleInterval
from matplotlib import pyplot as plt
from mpl_point_clicker import clicker
from photutils.detection import DAOStarFinder
from pyraf import iraf
from sep import Background, extract as sep_extract
from ccdproc import cosmicray_lacosmic

from .base_logger import logger
from .errors import AlignError, ImageCountError, NumberOfElementError
from .utils import Check, Fixer


class Fits:
    def __init__(self, path: Path):
        """
        Constructor method.
        Creates a Fits Object. The file_path must exist.

        Parameters
        ----------
        path: pathlib.Path
            Path object of the fits file.
        """
        self.NAME = self.__class__.__name__
        logger.info(f"Creating an instance from {self.NAME}")
        if not path.exists():
            raise FileNotFoundError("File does not exist")

        self.path = path

        iraf.noao(Stdout=PIPE)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(@: {id(self)}, file: {abs(self)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __abs__(self) -> str:
        return str(self.path.absolute())

    def __sub__(self, other: Union[Fits, float, int]) -> Fits:
        return self.imarith(other, "-")

    def __add__(self, other: Union[Fits, float, int]) -> Fits:
        return self.imarith(other, "+")

    def __radd__(self, other: Union[Fits, float, int]) -> Fits:
        return self.imarith(other, "+")

    def __mul__(self, other: Union[Fits, float, int]) -> Fits:
        return self.imarith(other, "*")

    def __rmul__(self, other: Union[Fits, float, int]) -> Fits:
        return self.imarith(other, "*")

    def __truediv__(self, other: Union[Fits, float, int]) -> Fits:
        return self.imarith(other, "/")

    @classmethod
    def from_path(cls, path: str) -> Fits:
        """
        Creates a Fits Object. The file_path must exist.

        Parameters
        ----------
        path: str
            Path of the fits file.

        Returns
        -------
        Fits
            Fits Object.
        """
        logger.info(f"Creating Fits from path. Parameters: {path=}")
        return Fits(Path(path))

    @property
    def file(self):
        return f"{{OBSCURED PATH}}/{str(self.path.stem)}{str(self.path.suffix)}"

    @property
    def imstat(self) -> dict:
        """
        Returns the npix, mean, stddev, min, max of the array as a dict. The default return of IRAF's imstatistics task.

        Returns
        -------
        dict
            Dictionary of statistics.
        """
        logger.info(f"imstat started. Parameters: None")

        iraf.imutil.imstatistics.unlearn()
        keys = ["npix", "mean", "stddev", "min", "max"]
        data = [each.split() for each in
                iraf.imutil.imstatistics(abs(self), fields="image,npix,mean,stddev,min,max", Stdout=PIPE)
                if not each.startswith("#") and not each.startswith("Error")]
        return {key: float(value) for key, value in zip(keys, data[0][1:])}

    @property
    def header(self) -> dict:
        """
        Returns the header of the fits file as a dict. The return of IRAF's imheader task with l+.

        Returns
        -------
        dict
            Dictionary of headers.
        """
        logger.info(f"Getting header. Parameters: None")

        header = fts.getheader(abs(self))
        return {i: header[i] for i in header if i}

    @property
    def data(self) -> np.ndarray:
        """
        Returns the header of the fits file as a np.array.

        Returns
        -------
        np.ndarray
            array of data.
        """
        logger.info(f"Getting data. Parameters: None")

        return fts.getdata(abs(self)).astype(float)

    def background(self, as_array: bool = False) -> Union[Background, np.ndarray]:
        """
        Returns the background object of the fits file.

        Parameters
        ----------
        as_array: bool
            If True returns a np.array of background. Otherwise, returns the object itself.

        Returns
        -------
        Union[Background, np.ndarray]
            Either a background object or a np.array.
        """
        logger.info(f"Getting background. Parameters: {as_array=}")

        if as_array:
            return Background(self.data).back()
        return Background(self.data)

    def cosmic_cleaner(self, output: str = None, override: bool = False, sigclip: float = 4.5, sigfrac: float = 0.3,
                       objlim: float = 5.0, gain: float = 1.0, readnoise: float = 6.5, satlevel: float = 65535.0,
                       pssl: float = 0.0, niter: int = 4, sepmed: bool = True, cleantype: str = 'meanmask',
                       fsmode: str = 'median', psfmodel: str = 'gauss', psffwhm: float = 2.5, psfsize: int = 7,
                       psfk: np.ndarray = None, psfbeta: float = 4.765, gain_apply: bool = True):
        """
        Returns consmic cleaned image.

        [1]: https://ccdproc.readthedocs.io/en/latest/api/ccdproc.cosmicray_lacosmic.html

        Parameters
        ----------
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            If True will overwrite the new_path if a file is already exists.
        sigclip: float, optional
            Laplacian-to-noise limit for cosmic ray detection. Lower values will flag more pixels as cosmic rays. Default: 4.5. see [1]
        sigfrac: float, optional
            Fractional detection limit for neighboring pixels. For cosmic ray neighbor pixels, a Laplacian-to-noise detection limit of sigfrac * sigclip will be used. Default: 0.3. see [1]
        objlim: float, optional
            Minimum contrast between Laplacian image and the fine structure image. Increase this value if cores of bright stars are flagged as cosmic rays. Default: 5.0. see [1]
        gain: float, optional
            Gain of the image (electrons / ADU). We always need to work in electrons for cosmic ray detection. Default: 1.0 see [1]
        readnoise: float, optional
            Read noise of the image (electrons). Used to generate the noise model of the image. Default: 6.5. see [1]
        satlevel: float, optional
            Saturation level of the image (electrons). This value is used to detect saturated stars and pixels at or above this level are added to the mask. Default: 65535.0. see [1]
        pssl: float, optional
            Previously subtracted sky level in ADU. We always need to work in electrons for cosmic ray detection, so we need to know the sky level that has been subtracted so we can add it back in. Default: 0.0. see [1]
        niter: float, optional
            Number of iterations of the LA Cosmic algorithm to perform. Default: 4. see [1]
        sepmed: int, optional
            Use the separable median filter instead of the full median filter. The separable median is not identical to the full median filter, but they are approximately the same, the separable median filter is significantly faster, and still detects cosmic rays well. Note, this is a performance feature, and not part of the original L.A. Cosmic. Default: True. see [1]
        cleantype: str, optional
            Set which clean algorithm is used: 1) "median": An unmasked 5x5 median filter. 2) "medmask": A masked 5x5 median filter. 3) "meanmask": A masked 5x5 mean filter. 4) "idw": A masked 5x5 inverse distance weighted interpolation. Default: "meanmask". see [1]
        fsmode: float, optional
            Method to build the fine structure image: 1) "median": Use the median filter in the standard LA Cosmic algorithm. 2) "convolve": Convolve the image with the psf kernel to calculate the fine structure image. Default: "median". see [1]
        psfmodel: str, optional
            Model to use to generate the psf kernel if fsmode == ‘convolve’ and psfk is None. The current choices are Gaussian and Moffat profiles: - "gauss" and "moffat" produce circular PSF kernels. - The "gaussx" and "gaussy" produce Gaussian kernels in the x and y directions respectively. Default: "gauss". see [1]
        psffwhm: float, optional
            Full Width Half Maximum of the PSF to use to generate the kernel. Default: 2.5. see [1]
        psfsize: int, optional
            Size of the kernel to calculate. Returned kernel will have size psfsize x psfsize. psfsize should be odd. Default: 7. see [1]
        psfk: np.ndarray (with float dtype), optional
            PSF kernel array to use for the fine structure image if fsmode == 'convolve'. If None and fsmode == 'convolve', we calculate the psf kernel using psfmodel. Default: None. see [1]
        psfbeta: float, optional
            Moffat beta parameter. Only used if fsmode=='convolve' and psfmodel=='moffat'. Default: 4.765.
        gain_apply: float, optional
            If True, return gain-corrected data, with correct units, otherwise do not gain-correct the data. Default is True to preserve backwards compatibility. see [1]

        Returns
        -------
        Fits
            Cleaned fits
        """
        logger.info(f"Starting Cosmic clean. Parameters: alot...")

        print(output)
        output = Fixer.output(output, override=override)
        print(output)

        newdata, _ = cosmicray_lacosmic(self.data, sigclip=sigclip, sigfrac=sigfrac, objlim=objlim, gain=gain,
                                        readnoise=readnoise, satlevel=satlevel, pssl=pssl, niter=niter, sepmed=sepmed,
                                        cleantype=cleantype, fsmode=fsmode, psfmodel=psfmodel, psffwhm=psffwhm,
                                        psfsize=psfsize, psfk=psfk, psfbeta=psfbeta, gain_apply=gain_apply)

        fts.writeto(output, newdata.value, header=fts.getheader(abs(self)))

        return Fits.from_path(output)

    def hedit(self, keys: Union[str, List[str]], values: Union[str, List[str]] = None, delete: bool = False,
              value_is_key: bool = False) -> None:
        """
        Edits header of the given file.

        Parameters
        ----------
        keys: str or List[str]
            Keys to be altered.
        values: str or List[str], optional
            Values to be added to set be set. Would be ignored if delete is True.
        delete: bool, optional
            Deletes the key from header if True.
        value_is_key: bool, optional
            Adds value of the key given in values if True. Would be ignored if delete is True.

        Returns
        -------
        None
            None.
        """
        logger.info(f"hedit started. Parameters: {keys=}, {values=}, {delete=}, {value_is_key=}, {keys=}")

        if delete:
            if isinstance(keys, str):
                keys = [keys]

            with fts.open(abs(self), "update") as hdu:
                for key in keys:
                    if key in hdu[0].header:
                        del hdu[0].header[key]
                    else:
                        logger.warning(f"{key} was not found in header. Skipping...")
        else:

            if not isinstance(values, type(keys)):
                logger.error(f"keys and values must both be strings or list of strings")
                raise ValueError("keys and values must both be strings or list of strings")

            if isinstance(keys, str):
                keys = [keys]

            if isinstance(values, str):
                values = [values]

            if len(keys) != len(values):
                logger.error(f"List of keys and values must be equal in length")
                raise ValueError("List of keys and values must be equal in length")

            with fts.open(abs(self), "update") as hdu:
                for key, value in zip(keys, values):
                    if value_is_key:
                        hdu[0].header[key] = hdu[0].header[value]
                    else:
                        hdu[0].header[key] = value

    def save_as(self, path: str, override: bool = False) -> Fits:
        """
        Saves the Fits file as new_path.

        Parameters
        ----------
        path: str
            New path to save the file.
        override: bool, optional
            If True will overwrite the new_path if a file is already exists.

        Returns
        -------
        Fits
            New fits object of saved fits file.
        """
        logger.info(f"saving as. Parameters: {path=}, {override=}")

        path = Fixer.output(path, override=override)

        iraf.imutil.imcopy.unlearn()
        iraf.imutil.imcopy(abs(self), path, verbose="no")

        return Fits.from_path(path)

    def imarith(self, other: Union[Fits, float, int], operand: str, output: str = None, override: bool = False) -> Fits:
        """
        Makes an arithmeic calculation on the file. The default behaviour of IRAF's imarith task.

        Parameters
        ----------
        other: Fits, float or int
            The value to be added to image array.
        operand: str
            An arithmetic operator. Either +, -, * or /.
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            If True will overwrite the new_path if a file is already exists.

        Returns
        -------
        Fits
            Fits object of resulting fits of the operation.
        """
        logger.info(f"imarith started. Parameters: {other=}, {operand=}, {output=}, {override=}")

        if not isinstance(other, (float, int, Fits)):
            logger.error(f"Please provide either a Fits Object or a numeric value")
            raise ValueError("Please provide either a Fits Object or a numeric value")

        Check.operand(operand)

        output = Fixer.output(output, override=override, delete=True, suffix=".fits", prefix="irony_")

        if isinstance(other, Fits):
            other = abs(other)

        iraf.imutil.imarith.unlearn()
        iraf.imutil.imarith(operand1=abs(self), op=operand, operand2=other, result=output)

        return Fits.from_path(output)

    def extract(self, detection_sigma: float = 5, min_area: float = 5):
        """
        Runs astroalign._find_sources to detect sources on the image.

        Parameters
        ----------
        detection_sigma: float
            `thresh = detection_sigma * bkg.globalrms`
        min_area: float
            Minimum area

        Returns
        -------
        pd.DataFrame
            List of sources found on the image.
        """
        bkg = self.background()
        thresh = detection_sigma * bkg.globalrms
        sources = sep_extract(self.data - bkg.back(), thresh, minarea=min_area)
        sources.sort(order="flux")
        if len(sources) < 0:
            raise NumberOfElementError("No source was found")

        return pd.DataFrame(
            sources,
            columns=["npix", "tnpix", "xmin", "xmax", "ymin", "ymax", "xcentroid", "ycentroid", "x2", "y2", "xy",
                     "errx2", "erry2", "errxy", "a", "b", "theta", "cxx", "cyy", "cxy", "cflux", "flux", "cpeak",
                     "peak", "xcpeak", "ycpeak", "xpeak", "ypeak", "flag"]
        )

    def daofind(self, sigma: float = 3, fwhm: float = 3, threshold: float = 5) -> pd.DataFrame:
        """
        Runs daofind to detect sources on the image.

        [1]: https://docs.astropy.org/en/stable/api/astropy.stats.sigma_clipped_stats.html

        [2]: https://photutils.readthedocs.io/en/stable/api/photutils.detection.DAOStarFinder.html

        Parameters
        ----------
        sigma: float, optional
            The number of standard deviations to use for both the lower and upper clipping limit. These limits are overridden by sigma_lower and sigma_upper, if input. The default is 3. [1]
        fwhm: float, optional
            The full-width half-maximum (FWHM) of the major axis of the Gaussian kernel in units of pixels. [2]
        threshold: float, optional
            The absolute image value above which to select sources. [2]

        Returns
        -------
        pd.DataFrame
            List of sources found on the image.
        """
        logger.info(
            f"daofind started. Parameters: {sigma=}, {fwhm=}, {threshold=}")

        mean, median, std = sigma_clipped_stats(self.data, sigma=sigma)
        daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold * std)
        sources = daofind(self.data - median)
        if sources is not None:
            return sources.to_pandas()
        return pd.DataFrame([],
                            columns=["id", "xcentroid", "ycentroid", "sharpness", "roundness1", "roundness2", "npix",
                                     "sky", "peak", "flux", "mag"])

    def align(self, other: Fits, output: str = None, max_control_points: int = 50, detection_sigma: float = 5,
              min_area: int = 5, override: bool = False) -> Fits:
        """
        Runs a Fits object of aligned Image.

        [1]: https://astroalign.quatrope.org/en/latest/api.html#astroalign.register

        Parameters
        ----------
        other: Fits
            The reference Image to be aligned as a Fits object.
        output: str, optional
            Path of the new fits file.
        max_control_points: int, optional
            The maximum number of control point-sources to find the transformation. [1]
        detection_sigma: int, optional
            Factor of background std-dev above which is considered a detection. [1]
        min_area: int, optional
            Minimum number of connected pixels to be considered a source. [1]
        override: bool, optional
            If True will overwrite the new_path if a file is already exists.

        Returns
        -------
        Fits
            Fits object of aligned image.
        """
        logger.info(
            f"align started. Parameters: {other=}, {output=}, {max_control_points=}, {detection_sigma=}, {min_area=}, {override=}")

        if not isinstance(other, Fits):
            logger.error("Other must be a Fits")
            raise ValueError("Other must be a Fits")

        output = Fixer.output(output, override=override)
        try:
            registered_image, footprint = astroalign.register(self.data, other.data,
                                                              max_control_points=max_control_points,
                                                              detection_sigma=detection_sigma, min_area=min_area)
            fts.writeto(output, registered_image, header=fts.getheader(abs(self)))
            return Fits.from_path(output)
        except ValueError:
            logger.error("Cannot align two images")
            raise AlignError("Cannot align two images")

    def show(self, points: pd.DataFrame = None, scale: bool = True) -> None:
        """
        Shows the Image using matplotlib.

        Parameters
        ----------
        points: pd.DataFrame, optional
            Draws points on image if a list is given.
        scale: bool, optional
            Scales the Image if True.

        Returns
        -------
        None
            None.
        """
        logger.info(f"showing image. Parameters: {points=}, {scale=}")

        if scale:
            zscale = ZScaleInterval()
        else:

            def zscale(x): return x

        plt.imshow(zscale(self.data), cmap="Greys_r")
        if points is not None:
            plt.scatter(points.xcentroid, points.ycentroid, s=10, c="red")
        plt.xticks([])
        plt.yticks([])
        plt.show()

    def solve_field(self, output: str = None, override: bool = False) -> None:
        # todo improve
        output = Fixer.output(output, override=override, delete=False)
        cmd = ["solve-field", str(self), "-o", output, "-p"]

        if override:
            cmd.append(override)

        process = subprocess.Popen(cmd)
        process.wait()

    def astrometry(self, api_key, solve_timeout=120):
        """
        Astrometry.net plate solving

        Parameters
        ----------
        api_key: str
            API Key
        solve_timeout: int
            Timeout

        Returns
        -------
        Fits
            Plate solved Fits object
        """
        pass
        # from astroquery.astrometry_net import AstrometryNet
        # ast = AstrometryNet()
        # ast.api_key = api_key
        #
        # try_again = True
        # submission_id = None
        #
        # while try_again:
        #     try:
        #         if not submission_id:
        #             wcs_header = ast.solve_from_image(abs(self),
        #                                               submission_id=submission_id)
        #         else:
        #             wcs_header = ast.monitor_submission(submission_id,
        #                                                 solve_timeout=solve_timeout)
        #     except TimeoutError as e:
        #         submission_id = e.args[1]
        #         print("="*82)
        #         print(e)
        #     else:
        #         try_again = False
        #
        # if wcs_header:
        #     print("asd")
        #     print(wcs_header)
        #     # with fts.open(abs(self), mode="update") as the_file:
        #     #     the_file[0].header.append(wcs_header)
        # else:
        #     print("dsa")
        #     print(wcs_header)

    def coordinate_picker(self, scale: bool = True) -> pd.DataFrame:
        """
        Shows the Image using matplotlib and returns a list of coordinates picked by user.

        Parameters
        ----------
        scale: bool, optional
            Scales the Image if True.

        Returns
        -------
        pd.DataFrame
            List of coordinates selected.
        """
        if scale:
            zscale = ZScaleInterval()
        else:

            def zscale(x):
                return x

        fig, ax = plt.subplots(constrained_layout=True)
        ax.imshow(zscale(self.data), cmap="Greys_r")
        klkr = clicker(ax, ["source"], markers=["o"])
        plt.show()
        if len(klkr.get_positions()["source"]) == 0:
            return pd.DataFrame([], columns=["xcentroid", "ycentroid"])

        return pd.DataFrame(
            klkr.get_positions()["source"], columns=[
                "xcentroid", "ycentroid"])


class FitsArray:
    def __init__(self, fits_list: List[Fits]) -> None:
        """
        Constructor method
        Creates a FitsArray Object. The length of  fits_lists must larger the 0.

        Parameters
        ----------
        fits_list: List[Fits]
            A list of Fits.
        """
        logger.info(f"Creating an instance from {self.__class__.__name__}")

        if not isinstance(fits_list, list):
            raise ValueError("fits_list must be a list of Fits")

        fits_list = [
            each
            for each in fits_list
            if isinstance(each, Fits)
        ]

        if len(fits_list) < 1:
            raise ImageCountError("No image was provided")

        self.fits_list = fits_list

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(@: {id(self)}, nof: {len(self)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __getitem__(self, key: int) -> Union[Fits, FitsArray]:
        element = self.fits_list[key]
        if isinstance(element, Fits):
            return element
        elif isinstance(element, List):
            return FitsArray(element)

        raise ValueError("Wrong slice")

    def __delitem__(self, key):
        del self.fits_list[key]

    def __len__(self) -> int:
        return len(self.fits_list)

    def __abs__(self) -> List[str]:
        return list(map(abs, self.fits_list))

    @classmethod
    def from_paths(cls, paths: List[str]) -> FitsArray:
        """
        Creates a FitsArray Object. The length of glob('file_path*.fit*') must be larger then 0.

        Parameters
        ----------
        paths: List[str]
            A list of strings of paths.

        Returns
        -------
        FitsArray
            FitsArray generated from list of paths as str.
        """
        logger.info(f"Creating FitsArray from from_paths. Parameters: {paths}")
        files = []
        for each in map(Path, paths):
            try:
                files.append(Fits(each))
            except FileNotFoundError:
                pass

        return FitsArray(files)

    @classmethod
    def from_pattern(cls, pattern: str) -> FitsArray:
        """
        Creates a FitsArray Object. The length of glob('file_path*.fit*') must be larger then 0.

        Parameters
        ----------
        pattern: str
            A pattern of a list of files.

        Returns
        -------
        FitsArray
            FitsArray generated from pattern of files.
        """
        logger.info(
            f"Creating FitsArray from from_paths. Parameters: {pattern}")

        return FitsArray.from_paths(glob(pattern))

    @contextlib.contextmanager
    def at_file(self) -> str:
        """
        Creates a text file with all fits file paths at each line. Useful for IRAF's @files.

        Returns
        -------
        str
            A context manager of a file containing file path of each file.
        """
        logger.info(f"Creating at_file. Parameters: None")

        with tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".fls", prefix="irony_") as tmp:
            to_write = []
            for each in self.fits_list:
                to_write.append(abs(each))
            tmp.write("\n".join(to_write))
            tmp.flush()
            yield tmp.name

    @property
    def files(self):
        return [fits.file for fits in self.fits_list]

    @property
    def imstat(self) -> pd.DataFrame:
        """
        Returns the npix, mean, stddev, min, max of the array as a pd.DataFrame. The default return of
        IRAF's imstatistics task.

        Returns
        -------
        pd.DataFrame
            List of statistics of all files.
        """
        logger.info(f"imstat started. Parameters: None")

        iraf.imutil.imstatistics.unlearn()
        with self.at_file() as at_file:
            return (pd.DataFrame([each.split() for each in
                                  iraf.imutil.imstatistics(f"@{at_file}", fields="image,npix,mean,stddev,min,max",
                                                           Stdout=PIPE) if
                                  not each.startswith("#") and not each.startswith("Error")],
                                 columns=("image", "npix", "mean", "stddev", "min", "max")).set_index("image").replace(
                {np.nan: None}).astype(float))

    @property
    def header(self) -> pd.DataFrame:
        """
        Returns the header of the fits file(s) as a pd.DataFrame. The return of IRAF's imheader task with l+.

        Returns
        -------
        pd.DataFrame
            List of headers of all files.
        """
        logger.info(f"getting header. Parameters: None")

        headers = []
        for each in self:
            h = each.header
            h["image"] = str(abs(each))
            headers.append(h)

        return pd.DataFrame(headers).set_index("image").replace({np.nan: None})

    def hedit(self, keys: Union[str, List[str]], values: Union[str, List[str]] = None, delete: bool = False,
              value_is_key: bool = False) -> None:
        """
        Edits header of the given file.

        Parameters
        ----------
        keys: str or List[str]
            Keys to be altered.
        values: str or List[str], optional
            Values to be added to set be set. Would be ignored if delete is True.
        delete: bool, optional
            Deletes the key from header if True.
        value_is_key: bool, optional
            Adds value of the key given in values if True. Would be ignored if delete is True.

        Returns
        -------
        None
            None.
        """
        logger.info(f"hedit started. Parameters: {keys=}, {values=}, {delete=}, {value_is_key=}")

        if delete:
            if isinstance(keys, str):
                keys = [keys]
            for fits in self:
                with fts.open(abs(fits), "update") as hdu:
                    for key in keys:
                        if key in hdu[0].header:
                            del hdu[0].header[key]
                        else:
                            logger.warning(f"{key} was not found in header. Skipping for {abs(fits)}")
        else:
            if not isinstance(keys, type(values)):
                logger.error(f"keys and values must both be strings or list of strings")
                raise ValueError("keys and values must both be strings or list of strings")

            if isinstance(keys, str):
                keys = [keys]
                values = [values]

            if len(keys) != len(values):
                logger.error(f"List of keys and values must be equal in length")
                raise ValueError("List of keys and values must be equal in length")

            for fits in self:
                with fts.open(abs(fits), "update") as hdu:
                    for key, value in zip(keys, values):
                        if value_is_key:
                            hdu[0].header[key] = hdu[0].header[value]
                        else:
                            hdu[0].header[key] = value

    def hselect(self, fields: Union[str, List[str]]) -> pd.DataFrame:
        """
        Returns the header of the fits file(s) as a pd.DataFrame. The return of IRAF's imheader task with l+.

        Parameters
        ----------
        fields: str or List[str]
            Keys to be returned.

        Returns
        -------
        pd.DataFrame
            List of selected headers of all files.
        """
        logger.info(f"hselect started. Parameters: {fields=}")

        if isinstance(fields, str):
            fields = [fields]

        fields_to_use = []
        headers = self.header

        for field in fields:
            if field in headers.columns:
                fields_to_use.append(field)
            else:
                logger.warning(f"{field} was not found in header. Skipping...")

        if len(fields_to_use) < 1:
            return pd.DataFrame()
        return self.header[fields_to_use]

    def imarith(self, other: Union[FitsArray, Fits, float, int, List[float], List[int]], operand: str,
                output: str = None) -> FitsArray:
        """
        Makes an arithmeic calculation on the file(s). The default behaviour of IRAF's imarith task.

        Parameters
        ----------
        other: FitsArray, List[float], List[int], Fits, float or int
            The value to be added to image array.
        operand: str
            An arithmetic operator. Either +, -, * or /.
        output: str, optional
            Path of the new fits files.

        Returns
        -------
        FitsArray
            FitsArray object of resulting fits of the operation.
        """
        logger.info(f"imarith started. Parameters: {other=}, {operand=}, {output=}")

        if not isinstance(other, (float, int, FitsArray, Fits, List)):
            logger.error(f"Please provide either a FitsArray Object, Fits Object or a numeric value")
            raise ValueError("Please provide either a FitsArray Object, Fits Object or a numeric value")

        Check.operand(operand)

        iraf.imutil.imarith.unlearn()
        with self.at_file() as self_at:
            with Fixer.to_new_directory(output, self) as new_at:
                if isinstance(other, (Fits, float, int)):
                    if isinstance(other, Fits):
                        other = abs(other)
                    iraf.imutil.imarith(operand1=f"'@{self_at}'", op=f"'{operand}'", operand2=f"'{other}'",
                                        result=f"'@{new_at}'", verbose="no")
                else:
                    if isinstance(other, FitsArray):
                        with other.at_file() as other_at:
                            iraf.imutil.imarith(operand1=f"'@{self_at}'", op=f"'{operand}'", operand2=f"'@{other_at}'",
                                                result=f"'@{new_at}'", verbose="no")
                    else:
                        with Fixer.at_file_from_list(other) as other_at:
                            iraf.imutil.imarith(operand1=f"'@{self_at}'", op=f"'{operand}'", operand2=f"'@{other_at}'",
                                                result=f"'@{new_at}'", verbose="no")

                with open(new_at, "r") as new_files:
                    return FitsArray.from_paths(new_files.read().split())

    def align(self, other: Fits, output: str = None, max_control_points: int = 50, detection_sigma: float = 5,
              min_area: int = 5) -> FitsArray:
        """
        Runs a FitsArray object of aligned Image.

        [1]: https://astroalign.quatrope.org/en/latest/api.html#astroalign.register

        Parameters
        ----------
        other: Fits
            The reference Image to be aligned as a Fits.
        output: str, optional
            Path of the new fits files.
        max_control_points: int, optional
            The maximum number of control point-sources to find the transformation. [1]
        detection_sigma: int, optional
            Factor of background std-dev above which is considered a detection. [1]
        min_area: int, optional
            Minimum number of connected pixels to be considered a source. [1]

        Returns
        -------
        FitsArray
            FitsArray object of aligned images.
        """
        logger.info(
            f"align started. Parameters: {other=}, {output=}, {max_control_points=}, {detection_sigma=}, {min_area=}")

        if not isinstance(other, Fits):
            logger.error("Other must be a Fits")
            raise ValueError("Other must be a Fits")

        with Fixer.to_new_directory(output, self) as new_files:
            with open(new_files, "r") as f2r:
                aligned_files = []
                new_files = f2r.readlines()
                for fits, new_file in zip(self, new_files):
                    try:
                        new_fits = fits.align(other, new_file.strip(), max_control_points=max_control_points,
                                              detection_sigma=detection_sigma, min_area=min_area)
                        aligned_files.append(abs(new_fits))
                    except astroalign.MaxIterError:
                        pass
                    except AlignError:
                        pass
            if len(aligned_files) < 1:
                logger.error(f"None of the input images could be aligned")
                raise ImageCountError("None of the input images could be aligned")
            return FitsArray.from_paths(aligned_files)

    def cosmic_cleaner(self, output: str = None, override: bool = False, sigclip: float = 4.5, sigfrac: float = 0.3,
                       objlim: float = 5.0, gain: float = 1.0, readnoise: float = 6.5, satlevel: float = 65535.0,
                       pssl: float = 0.0, niter: int = 4, sepmed: bool = True, cleantype: str = 'meanmask',
                       fsmode: str = 'median', psfmodel: str = 'gauss', psffwhm: float = 2.5, psfsize: int = 7,
                       psfk: np.ndarray = None, psfbeta: float = 4.765, gain_apply: bool = True):
        """
        Returns consmic cleaned image array.

        [1]: https://ccdproc.readthedocs.io/en/latest/api/ccdproc.cosmicray_lacosmic.html

        Parameters
        ----------
        output: str, optional
            Path of the new fits file.
        override: bool, optional
            If True will overwrite the new_path if a file is already exists.
        sigclip: float, optional
            Laplacian-to-noise limit for cosmic ray detection. Lower values will flag more pixels as cosmic rays. Default: 4.5. see [1]
        sigfrac: float, optional
            Fractional detection limit for neighboring pixels. For cosmic ray neighbor pixels, a Laplacian-to-noise detection limit of sigfrac * sigclip will be used. Default: 0.3. see [1]
        objlim: float, optional
            Minimum contrast between Laplacian image and the fine structure image. Increase this value if cores of bright stars are flagged as cosmic rays. Default: 5.0. see [1]
        gain: float, optional
            Gain of the image (electrons / ADU). We always need to work in electrons for cosmic ray detection. Default: 1.0 see [1]
        readnoise: float, optional
            Read noise of the image (electrons). Used to generate the noise model of the image. Default: 6.5. see [1]
        satlevel: float, optional
            Saturation level of the image (electrons). This value is used to detect saturated stars and pixels at or above this level are added to the mask. Default: 65535.0. see [1]
        pssl: float, optional
            Previously subtracted sky level in ADU. We always need to work in electrons for cosmic ray detection, so we need to know the sky level that has been subtracted so we can add it back in. Default: 0.0. see [1]
        niter: int, optional
            Number of iterations of the LA Cosmic algorithm to perform. Default: 4. see [1]
        sepmed: float, optional
            Use the separable median filter instead of the full median filter. The separable median is not identical to the full median filter, but they are approximately the same, the separable median filter is significantly faster, and still detects cosmic rays well. Note, this is a performance feature, and not part of the original L.A. Cosmic. Default: True. see [1]
        cleantype: str, optional
            Set which clean algorithm is used: 1) "median": An unmasked 5x5 median filter. 2) "medmask": A masked 5x5 median filter. 3) "meanmask": A masked 5x5 mean filter. 4) "idw": A masked 5x5 inverse distance weighted interpolation. Default: "meanmask". see [1]
        fsmode: float, optional
            Method to build the fine structure image: 1) "median": Use the median filter in the standard LA Cosmic algorithm. 2) "convolve": Convolve the image with the psf kernel to calculate the fine structure image. Default: "median". see [1]
        psfmodel: str, optional
            Model to use to generate the psf kernel if fsmode == ‘convolve’ and psfk is None. The current choices are Gaussian and Moffat profiles: - "gauss" and "moffat" produce circular PSF kernels. - The "gaussx" and "gaussy" produce Gaussian kernels in the x and y directions respectively. Default: "gauss". see [1]
        psffwhm: float, optional
            Full Width Half Maximum of the PSF to use to generate the kernel. Default: 2.5. see [1]
        psfsize: int, optional
            Size of the kernel to calculate. Returned kernel will have size psfsize x psfsize. psfsize should be odd. Default: 7. see [1]
        psfk: np.ndarray (with float dtype), optional
            PSF kernel array to use for the fine structure image if fsmode == 'convolve'. If None and fsmode == 'convolve', we calculate the psf kernel using psfmodel. Default: None. see [1]
        psfbeta: float, optional
            Moffat beta parameter. Only used if fsmode=='convolve' and psfmodel=='moffat'. Default: 4.765.
        gain_apply: int, optional
            If True, return gain-corrected data, with correct units, otherwise do not gain-correct the data. Default is True to preserve backwards compatibility. see [1]

        Returns
        -------
            FitsArray
            Cleaned FitsArray
        """
        logger.info(f"Starting Cosmic clean. Parameters: alot...")

        with Fixer.to_new_directory(output, self) as new_files:
            with open(new_files, "r") as f2r:
                cleaned_files = []
                new_files = f2r.read().split()
                for fits, new_file in zip(self, new_files):
                    try:

                        new_fits = fits.cosmic_cleaner(output=new_file, override=override, sigclip=sigclip,
                                                       sigfrac=sigfrac, objlim=objlim, gain=gain, readnoise=readnoise,
                                                       satlevel=satlevel, pssl=pssl, niter=niter, sepmed=sepmed,
                                                       cleantype=cleantype, fsmode=fsmode, psfmodel=psfmodel,
                                                       psffwhm=psffwhm, psfsize=psfsize, psfk=psfk, psfbeta=psfbeta,
                                                       gain_apply=gain_apply)
                        cleaned_files.append(abs(new_fits))
                    except astroalign.MaxIterError:
                        pass
                    except AlignError:
                        pass
            if len(cleaned_files) < 1:
                logger.error(f"None of the input images could be cleaned")
                raise ImageCountError("None of the input images could be cleaned")
            return FitsArray.from_paths(cleaned_files)

    def show(self, scale: bool = True, interval: float = 1):
        """
        Animates the Images using matplotlib.

        Parameters
        ----------
        scale: bool, optional
            Scales the Image if True.
        interval: float, optional
            Interval of the animation. The smaller the value the faster the animation.

        Returns
        -------
        None
            None.
        """
        logger.info(f"animating images. Parameters: {scale=}, {interval=}")

        fig = plt.figure()

        if scale:
            zscale = ZScaleInterval()
        else:

            def zscale(x):
                return x

        im = plt.imshow(zscale(self[0].data), cmap="Greys_r", animated=True)
        plt.xticks([])
        plt.yticks([])

        def updatefig(args):
            im.set_array(zscale(self[args % len(self)].data))
            return im,

        _ = animation.FuncAnimation(fig, updatefig, interval=interval, blit=True)
        plt.show()

    def groupby(self, groups: Union[str, List[str]]) -> Dict[Hashable, FitsArray]:
        """
        Groups FitsArray by given key in header. Returns a dict with tuple of keys as key and FitsArray as value.
        
        Parameters
        ----------
        groups: str or List[str]
            Key(s).

        Returns
        -------
        dict
            A dictionary of grouped images.
        """
        logger.info(f"groupby started. Parameters: {groups=}")

        if isinstance(groups, str):
            groups = [groups]

        if len(groups) < 1:
            return dict()

        headers = self.header
        for group in groups:
            if group not in headers.columns:
                headers[group] = "N/A"

        grouped = {}
        for keys, df in headers.fillna("N/A").groupby(groups, dropna=False):
            grouped[keys] = FitsArray.from_paths(df.index.tolist())

        return grouped

    def save_as(self, output: str) -> FitsArray:
        """
        Saves the FitsArray files to output.

        Parameters
        ----------
        output: str
            New directory to save files.

        Returns
        -------
        FitsArray
            New FitsArray object of saved fits files.
        """
        logger.info(f"saving as. Parameters: {output=}")
        with self.at_file() as self_at:
            with Fixer.to_new_directory(output, self) as new_at:
                iraf.imutil.imcopy.unlearn()
                iraf.imutil.imcopy(f"'@{self_at}'", f"'@{new_at}'", verbose="no")

                with open(new_at, "r") as new_files:
                    return FitsArray.from_paths(new_files.read().split())
