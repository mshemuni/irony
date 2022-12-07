from __future__ import annotations

import contextlib
import tempfile
from glob import glob
from pathlib import Path
from subprocess import PIPE
from typing import Dict, List, Union, Iterator, Hashable

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
from sep import Background

from .base_logger import logger
from .errors import AlignError, ImageCountError
from .utils import Check, Fixer


class Fits:
    """
    Fits(Path('file_path'))

    Creates a Fits Object
    The `file_path` must exist.
    
    :param path: A Path object of a Fits file
    :type path: Path

    """

    def __init__(self, path: Path):
        """Constructor method
        """
        logger.info(f"Creating an instance from {self.__class__.__name__}")
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

    @classmethod
    def from_path(cls, path: str) -> Fits:
        """
        Fits.from_path('file_path')

        Creates a Fits Object
        The `file_path` must exist.
        
        :param path: A path of a Fits file
        :type path: str

        :return: Fits Object
        :rtype: Fits
        """
        logger.info(f"Creating Fits from path. Parameters: {path=}")
        return Fits(Path(path))

    @property
    def imstat(self) -> dict:
        """
        fts = Fits.from_path('file_path')
        fts.imstat

        returns the `npix`, `mean`, `stddev`, `min`, `max` of the array as a dict. The default return of IRAF's
        `imstatistics` task.

        :return: dictionary of statistics
        :rtype: dict
        """
        logger.info(f"imstat started. Parameters: None")

        iraf.imutil.imstatistics.unlearn()
        keys = ["npix", "mean", "stddev", "min", "max"]
        data = [
            each.split()
            for each in iraf.imutil.imstatistics(
                abs(self), fields="image,npix,mean,stddev,min,max", Stdout=PIPE
            )
            if not each.startswith("#") and not each.startswith("Error")
        ]
        return {key: float(value) for key, value in zip(keys, data[0][1:])}

    @property
    def header(self) -> dict:
        """
        fts = Fits.from_path('file_path')
        fts.header

        returns the header of the fits file as a dict. The return of IRAF's `imheader` task with `l+`.

        :return: dictionary of headers
        :rtype: dict
        """
        logger.info(f"Getting header. Parameters: None")

        header = fts.getheader(abs(self))
        return {i: header[i] for i in header if i}

    @property
    def data(self) -> np.ndarray:
        """
        fts = Fits.from_path('file_path')
        fts.data

        returns the header of the fits file as a np.array.

        :return: array of data
        :rtype: np.ndarray
        """
        logger.info(f"Getting data. Parameters: None")

        return fts.getdata(abs(self)).astype(float)

    def background(
            self, as_array: bool = False) -> Union[Background, np.ndarray]:
        """
        fts = Fits.from_path('file_path')
        fts.background()

        returns the background object of the fits file.
        
        :param as_array: If `True` returns a np.array of background. Otherwise, returns the object itself.
        :type as_array: bool

        :return: Either a background Object or a np.array
        :rtype: Union[Background, np.ndarray]
        """
        logger.info(f"Getting background. Parameters: {as_array=}")

        if as_array:
            return Background(self.data).back()
        return Background(self.data)

    def hedit(
        self,
        keys: Union[str, List[str]],
        values: Union[str, List[str], None] = None,
        delete: bool = False,
        value_is_key: bool = False,
    ) -> None:
        """
        fts = Fits.from_path('file_path')
        fts.hedit()

        Edits header of the given file.
        
        :param keys: Keys to be altered
        :type keys: str or List[str]
        
        :param values: values to be added to set be set. Would be ignored if `delete` is `True`.
        :type values: str or List[str] (, optional)
        
        :param delete: deletes the key from header if `True`.
        :type delete: bool (, optional)

        :param value_is_key: adds value of the key given in `values` if `True`. Would be ignored if `delete` is `True`.
        :type value_is_key: bool (, optional)

        :return: none
        :rtype: None
        """
        logger.info(
            f"hedit started. Parameters: {keys=}, {values=}, {delete=}, {value_is_key=}, {keys=}"
        )

        if delete:
            if isinstance(keys, str):
                keys = [keys]

            with fts.open(abs(self), "update") as hdu:
                for key in keys:
                    if key in hdu[0].header:
                        del hdu[0].header[key]
        else:

            if not isinstance(values, type(keys)):
                logger.error(
                    f"keys and values must both be strings or list of strings")
                raise ValueError(
                    "keys and values must both be strings or list of strings"
                )

            if isinstance(keys, str):
                keys = [keys]

            if isinstance(values, str):
                values = [values]

            if len(keys) != len(values):
                logger.error(
                    f"List of keys and values must be equal in length")
                raise ValueError(
                    "List of keys and values must be equal in length")

            with fts.open(abs(self), "update") as hdu:
                for key, value in zip(keys, values):
                    if value_is_key:
                        hdu[0].header[key] = hdu[0].header[value]
                    else:
                        hdu[0].header[key] = value

    def save_as(self, path: str, override: bool = False) -> Fits:
        """
        fts = Fits.from_path('file_path')
        fts.save_as('new_path')

        Saves the Fits file as `new_path`
        
        :param path: new path to save the file
        :type path: str
        
        :param override: If `True` will overwrite the `new_path` if a file is already exists.
        :type override: bool (, optional)

        :return: new Fits object of saved fits file
        :rtype: Fits
        """
        logger.info(f"saving as. Parameters: {path=}, {override=}")

        path = Fixer.output(path, override=override)

        iraf.imutil.imcopy.unlearn()
        iraf.imutil.imcopy(abs(self), path, verbose="no")

        return Fits.from_path(path)

    def imarith(
        self,
        other: Union[Fits, float, int],
        operand: str,
        output: Union[str, None] = None,
        override: bool = False,
    ) -> Fits:
        """
        fts = Fits.from_path('file_path')
        fts.imarith(other, operand)

        makes an arithmeic calculation on the file. The default behaviour of IRAF's `imarith` task.

        :param other: the value to be added to image array.
        :type other: Fits or float or int
        
        :param operand: An arithmetic operator. Either `+`, `-`, `*` or `/`
        :type operand: str
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param override: If `True` will overwrite the `new_path` if a file is already exists.
        :type override: bool (, optional)

        :return: Fits object of resulting fits of the operation
        :rtype: Fits
        """
        logger.info(
            f"imarith started. Parameters: {other=}, {operand=}, {output=}, {override=}"
        )

        if not isinstance(other, (float, int, Fits)):
            logger.error(
                f"Please provide either a Fits Object or a numeric value")
            raise ValueError(
                "Please provide either a Fits Object or a numeric value")

        Check.operand(operand)

        output = Fixer.output(
            output,
            override=override,
            delete=True,
            suffix=".fits",
            prefix="piron_")

        if isinstance(other, Fits):
            other = abs(other)

        iraf.imutil.imarith.unlearn()
        iraf.imutil.imarith(
            operand1=abs(self), op=operand, operand2=other, result=output
        )

        return Fits.from_path(output)

    def daofind(
        self, sigma: float = 3, fwhm: float = 3, threshold: float = 5
    ) -> pd.DataFrame:
        """
        fts = Fits.from_path('file_path')
        fts.daofind()

        Runs daofind to detect sources on the image.
        
        :param sigma: The number of standard deviations to use for both the lower and upper clipping limit. These
        limits are overridden by sigma_lower and sigma_upper, if input. The default is 3. [1] :type sigma: float (,
        optional)
        
        :param fwhm: The full-width half-maximum (FWHM) of the major axis of the Gaussian kernel in units of pixels. [2]
        :type fwhm: float (, optional)
        
        :param threshold: The absolute image value above which to select sources. [2]
        :type threshold: float (, optional)

        [1]: https://docs.astropy.org/en/stable/api/astropy.stats.sigma_clipped_stats.html
        [2]: https://photutils.readthedocs.io/en/stable/api/photutils.detection.DAOStarFinder.html

        :return: List of sources found on the image
        :rtype: pd.DataFrame
        """
        logger.info(
            f"daofind started. Parameters: {sigma=}, {fwhm=}, {threshold=}")

        mean, median, std = sigma_clipped_stats(self.data, sigma=sigma)
        daofind = DAOStarFinder(fwhm=fwhm, threshold=threshold * std)
        sources = daofind(self.data - median)
        if sources is not None:
            return sources.to_pandas()
        return pd.DataFrame(
            [],
            columns=[
                "id",
                "xcentroid",
                "ycentroid",
                "sharpness",
                "roundness1",
                "roundness2",
                "npix",
                "sky",
                "peak",
                "flux",
                "mag",
            ],
        )

    def align(
        self,
        other: Fits,
        output: Union[str, None] = None,
        max_control_points: int = 50,
        detection_sigma: float = 5,
        min_area: int = 5,
        override: bool = False,
    ) -> Fits:
        """
        fts = Fits.from_path('file_path')
        other = Fits.from_path('another_file_path')
        fts.daofind(other)

        Runs a Fits object of aligned Image.
        
        :param other: The reference Image to be aligned as a Fits object
        :type other: Fits
        
        :param output: path of the new fits file.
        :type output: str (, optional)
        
        :param max_control_points: The maximum number of control point-sources to find the transformation. [1]
        :type max_control_points: int (, optional)
        
        :param detection_sigma: Factor of background std-dev above which is considered a detection. [1]
        :type detection_sigma: int (, optional)
        
        :param min_area: Minimum number of connected pixels to be considered a source. [1]
        :type min_area: int (, optional)
        
        :param override: If `True` will overwrite the `new_path` if a file is already exists.
        :type override: bool (, optional)

        [1]: https://astroalign.quatrope.org/en/latest/api.html#astroalign.register

        :return: Fits object of aligned image
        :rtype: Fits

        """
        logger.info(
            f"align started. Parameters: {other=}, {output=}, {max_control_points=}, {detection_sigma=}"
            f", {min_area=}, {override=} "
        )

        output = Fixer.output(output, override=override)
        try:
            registered_image, footprint = astroalign.register(
                self.data,
                other.data,
                max_control_points=max_control_points,
                detection_sigma=detection_sigma,
                min_area=min_area,
            )
            fts.writeto(
                output,
                registered_image,
                header=fts.getheader(
                    abs(self)))
            return Fits.from_path(output)
        except ValueError:
            raise AlignError("Cannot align two images")

    def show(self, points: Union[pd.DataFrame, None] = None, scale: bool = True) -> None:
        """
        fts = Fits.from_path('file_path')
        fts.show()

        Shows the Image using matplotlib.
        
        :param points: Draws points on image if a list is given
        :type points: pd.DataFrame (, optional)
        
        :param scale: Scales the Image if `True`
        :type scale: bool (, optional)

        :return: none
        :rtype: None
        """
        logger.info(f"showing image. Parameters: {points=}, {scale=}")

        if scale:
            zscale = ZScaleInterval()
        else:

            def zscale(x):
                return x

        plt.imshow(zscale(self.data), cmap="Greys_r")
        if points is not None:
            plt.scatter(points.xcentroid, points.ycentroid, s=10, c="red")
        plt.xticks([])
        plt.yticks([])
        plt.show()

    def coordinate_picker(self, scale: bool = True):
        """
        fts = Fits.from_path('file_path')
        fts.coordinate_picker()

        Shows the Image using matplotlib and returns a list of coordinates picked by user
        
        :param scale: Scales the Image if `True`
        :type scale: bool (, optional)

        :return: none
        :rtype: None
        """
        if scale:
            zscale = ZScaleInterval()
        else:

            def zscale(x):
                return x

        fig, ax = plt.subplots(constrained_layout=True)
        ax.imshow(zscale(self.data), cmap="Greys_r")
        klkr = clicker(ax, ["source"], markers=["x"])
        plt.show()
        if len(klkr.get_positions()["source"]) == 0:
            return pd.DataFrame([], columns=["xcentroid", "ycentroid"])

        return pd.DataFrame(
            klkr.get_positions()["source"], columns=[
                "xcentroid", "ycentroid"])


class FitsArray:
    """
    FitsArray([Path('file_path1'), Path('file_path2'), ...])

    Creates a FitsArray Object
    The length of  `fits_list`s must larger the 0.
    
    :param fits_list: A list of Fits
    :type fits_list: List[Fits]
    """

    def __init__(self, fits_list: List[Fits]) -> None:
        """Constructor method
        """
        logger.info(f"Creating an instance from {self.__class__.__name__}")

        if len(fits_list) < 1:
            raise ImageCountError("No image was provided")

        self.fits_list = fits_list

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(@: {id(self)}, nof: {len(self)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __getitem__(self, key: int) -> Fits:
        return self.fits_list[key]

    def __len__(self) -> int:
        return len(self.fits_list)

    def __abs__(self) -> List[str]:
        return list(map(abs, self.fits_list))

    @classmethod
    def from_paths(cls, paths: List[str]) -> FitsArray:
        """
        FitsArray.from_paths(glob('file_path*.fit*'))

        Creates a FitsArray Object
        The length of `glob('file_path*.fit*')` must be larger then 0.
        
        :param paths: A list of strings of paths
        :type paths: List[str]

        :return: FitsArray generated from list of paths as str
        :rtype: FitsArray
        """
        logger.info(f"Creating FitsArray from from_paths. Parameters: {paths}")
        files = []
        for each in map(Path, paths):
            try:
                files.append(Fits(each))
            except FileNotFoundError:
                pass

        return FitsArray(list(files))

    @classmethod
    def from_pattern(cls, pattern: str) -> FitsArray:
        """
        FitsArray.from_pattern('file_path*.fit*')

        Creates a FitsArray Object
        The length of `glob('file_path*.fit*')` must be larger then 0.
        
        :param pattern: a pattern of a list of files
        :type pattern: str

        :return: FitsArray generated from pattern of files
        :rtype: FitsArray
        """
        logger.info(
            f"Creating FitsArray from from_paths. Parameters: {pattern}")

        return FitsArray(list(map(Fits, map(Path, glob(pattern)))))

    @contextlib.contextmanager
    def at_file(self) -> Iterator[str]:
        """
        fa = FitsArray.from_paths(glob('file_path*.fit*'))
        with fa.at_file() as at_file:
            # Use at_file for
            pass

        Creates a text file with all fits file paths at each line. Useful for IRAF's `@file`s.

        :return: a context manager of an a file containing file path of each file
        :rtype: Generator[str]
        """
        logger.info(f"Creating at_file. Parameters: None")

        with tempfile.NamedTemporaryFile(
            mode="w", delete=True, suffix=".fls", prefix="piron_"
        ) as tmp:
            to_write = []
            for each in self.fits_list:
                to_write.append(abs(each))
            tmp.write("\n".join(to_write))
            tmp.flush()
            yield tmp.name

    @property
    def imstat(self) -> pd.DataFrame:
        """
        fa = FitsArray.from_pattern('pattern')
        fa.imstat

        returns the `npix`, `mean`, `stddev`, `min`, `max` of the array as a pd.DataFrame. The default return of
        IRAF's `imstatistics` task.

        :return: List of statistics of all files
        :rtype: pd.DataFrame
        """
        logger.info(f"imstat started. Parameters: None")

        iraf.imutil.imstatistics.unlearn()
        with self.at_file() as at_file:
            return (
                pd.DataFrame(
                    [
                        each.split() for each in iraf.imutil.imstatistics(
                            f"@{at_file}",
                            fields="image,npix,mean,stddev,min,max",
                            Stdout=PIPE,
                        ) if not each.startswith("#") and not each.startswith("Error")],
                    columns=(
                        "image",
                        "npix",
                        "mean",
                        "stddev",
                        "min",
                        "max"),
                ) .set_index("image") .replace(
                    {
                        np.nan: None}) .astype(float))

    @property
    def header(self) -> pd.DataFrame:
        """
        fa = FitsArray.from_pattern('pattern')
        fa.header

        returns the header of the fits file(s) as a pd.DataFrame. The return of IRAF's `imheader` task with `l+`.

        :return: List of headers of all files
        :rtype: pd.DataFrame
        """
        logger.info(f"getting header. Parameters: None")

        headers = []
        for each in self:
            h = each.header
            h["image"] = str(abs(each))
            headers.append(h)

        return pd.DataFrame(headers).set_index("image").replace({np.nan: None})

    def hedit(
        self,
        keys: Union[str, List[str]],
        values: Union[str, List[str]] = None,
        delete: bool = False,
        value_is_key: bool = False,
    ) -> None:
        """
        fa = FitsArray.from_pattern('pattern')
        fa.hedit("key", "value")

        Edits header of the given file.
        
        :param keys: Keys to be altered
        :type keys: str or List[str]
        
        :param values: values to be added to set be set. Would be ignored if `delete` is `True`.
        :type values: str or List[str] (, optional)
        
        :param delete: deletes the key from header if `True`.
        :type delete: bool (, optional)
        
        :param value_is_key: adds value of the key given in `values` if `True`. Would be ignored if `delete` is `True`.
        :type value_is_key: bool (, optional)

        :return: none
        :rtype: None
        """
        logger.info(
            f"hedit started. Parameters: {keys=}, {values=}, {delete=}, {value_is_key=}"
        )

        if delete:
            if isinstance(keys, str):
                keys = [keys]
            for fits in self:
                with fts.open(abs(fits), "update") as hdu:
                    for key in keys:
                        if key in hdu[0].header:
                            del hdu[0].header[key]
        else:
            if not isinstance(keys, type(values)):
                logger.error(
                    f"keys and values must both be strings or list of strings")
                raise ValueError(
                    "keys and values must both be strings or list of strings"
                )

            if isinstance(keys, str):
                keys = [keys]
                values = [values]

            if len(keys) != len(values):
                logger.error(
                    f"List of keys and values must be equal in length")
                raise ValueError(
                    "List of keys and values must be equal in length")

            for fits in self:
                with fts.open(abs(fits), "update") as hdu:
                    for key, value in zip(keys, values):
                        if value_is_key:
                            hdu[0].header[key] = hdu[0].header[value]
                        else:
                            hdu[0].header[key] = value

    def hselect(self, fields: Union[str, List[str]]) -> pd.DataFrame:
        """
        fa = FitsArray.from_pattern('pattern')
        fa.hselect("key1")
        fa.hselect(["key1", "key2", "key3"])

        returns the header of the fits file(s) as a pd.DataFrame. The return of IRAF's `imheader` task with `l+`.
        
        :param fields: Keys to be returned
        :type fields: str or List[str]

        :return: List of selected headers of all files
        :rtype: pd.DataFrame
        """
        logger.info(f"hselect started. Parameters: {fields=}")

        if isinstance(fields, str):
            fields = [fields]

        fields_to_use = []
        headers = self.header

        for field in fields:
            if field in headers.columns:
                fields_to_use.append(field)

        if len(fields_to_use) < 1:
            return pd.DataFrame()
        return self.header[fields_to_use]

    def imarith(
        self,
        other: Union[FitsArray, Fits, float, int, List[float], List[int]],
        operand: str,
        output: str = None,
    ) -> FitsArray:
        """
        fa = FitsArray.from_pattern('pattern')
        fa.imarith(other, operand)

        makes an arithmeic calculation on the file file(s). The default behaviour of IRAF's `imarith` task.
        
        :param other: the value to be added to image array.
        :type other: FitsArray, List[float], List[int], Fits, float or int

        :param operand: An arithmetic operator. Either `+`, `-`, `*` or `/`
        :type operand: str

        :param output: path of the new fits files.
        :type output: str (, optional)

        :return: FitsArray object of resulting fits of the operation
        :rtype: FitsArray
        """
        logger.info(
            f"imarith started. Parameters: {other=}, {operand=}, {output=}")

        if not isinstance(other, (float, int, FitsArray, Fits, List)):
            logger.error(
                f"Please provide either a FitsArray Object, Fits Object or a numeric value"
            )
            raise ValueError(
                "Please provide either a FitsArray Object, Fits Object or a numeric value"
            )

        Check.operand(operand)

        iraf.imutil.imarith.unlearn()
        with self.at_file() as self_at:
            with Fixer.to_new_directory(output, self) as new_at:
                if isinstance(other, (Fits, float, int)):
                    if isinstance(other, Fits):
                        other = abs(other)
                    iraf.imutil.imarith(
                        operand1=f"'@{self_at}'",
                        op=f"'{operand}'",
                        operand2=f"'{other}'",
                        result=f"'@{new_at}'",
                        verbose="no",
                    )
                else:
                    if isinstance(other, FitsArray):
                        with other.at_file() as other_at:
                            iraf.imutil.imarith(
                                operand1=f"'@{self_at}'",
                                op=f"'{operand}'",
                                operand2=f"'@{other_at}'",
                                result=f"'@{new_at}'",
                                verbose="no",
                            )
                    else:
                        with Fixer.at_file_from_list(other) as other_at:
                            iraf.imutil.imarith(
                                operand1=f"'@{self_at}'",
                                op=f"'{operand}'",
                                operand2=f"'@{other_at}'",
                                result=f"'@{new_at}'",
                                verbose="no",
                            )

                with open(new_at, "r") as new_files:
                    return FitsArray.from_paths(new_files.read().split())

    def align(
        self,
        other: Fits,
        output: str = None,
        max_control_points: int = 50,
        detection_sigma: float = 5,
        min_area: int = 5,
    ) -> FitsArray:
        """
        fa = FitsArray.from_pattern('pattern')
        fts.daofind(fa[0])

        Runs a FitsArray object of aligned Image.

        :param other: The reference Image to be aligned as a Fits 
        :type other: Fits

        :param output: path of the new fits files.
        :type output: str (, optional)
        
        :param max_control_points: The maximum number of control point-sources to find the transformation. [1]
        :type max_control_points: int (, optional)
        
        :param detection_sigma: Factor of background std-dev above which is considered a detection. [1]
        :type detection_sigma: int (, optional)
        
        :param min_area: Minimum number of connected pixels to be considered a source. [1]
        :type min_area: int (, optional)

        [1]: https://astroalign.quatrope.org/en/latest/api.html#astroalign.register

        :return: FitsArray object of aligned images
        :rtype: FitsArray
        """
        logger.info(
            f"align started. Parameters: {other=}, {output=}, {max_control_points=}, {detection_sigma=}, {min_area=}"
        )

        with Fixer.to_new_directory(output, self) as new_files:
            with open(new_files, "r") as f2r:
                aligned_files = []
                new_files = f2r.readlines()
                for fits, new_file in zip(self, new_files):
                    try:
                        new_fits = fits.align(
                            other,
                            new_file.strip(),
                            max_control_points=max_control_points,
                            detection_sigma=detection_sigma,
                            min_area=min_area,
                        )
                        aligned_files.append(abs(new_fits))
                    except astroalign.MaxIterError:
                        pass
                    except AlignError:
                        pass
            if len(aligned_files) < 1:
                logger.error(f"None of the input images could be aligned")
                raise ImageCountError(
                    "None of the input images could be aligned")
            return FitsArray.from_paths(aligned_files)

    def show(self, scale: bool = True, interval: float = 1):
        """
        fa = FitsArray.from_pattern('pattern')
        fa.show()

        Animates the Images using matplotlib.
        
        :param scale: Scales the Image if `True`
        :type scale: bool (, optional)
        
        :param interval: Interval of the animation. The smaller the value the faster the animation.
        :type interval: float (, optional)

        :return: none
        :rtype: None
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

        _ = animation.FuncAnimation(
            fig, updatefig, interval=interval, blit=True)
        plt.show()

    def groupby(
        self, groups: Union[str, List[str]]
    ) -> Dict[Hashable, FitsArray]:
        """
        fa = FitsArray.from_pattern('pattern')
        fa.groupby("key")
        fa.groupby(["key1", "key2", "key3"])

        Groups FitsArray by given key in header.
        returns a dict with tuple of keys as key and FitsArray as value
        
        :param groups: Key(s)
        :type groups: str or List[str]

        :return: a dictionary of grouped images
        :rtype: dict
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
        fa = FitsArray.from_pattern('pattern')
        fa.save_as('new_path')

        Saves the FitsArray files as `output`
        
        :param output: new directory to save files
        :type output: str

        :return: new FitsArray object of saved fits files
        :rtype: FitsArray
        """
        logger.info(f"saving as. Parameters: {output=}")
        with self.at_file() as self_at:
            with Fixer.to_new_directory(output, self) as new_at:

                iraf.imutil.imcopy.unlearn()
                iraf.imutil.imcopy(
                    f"'@{self_at}'", f"'@{new_at}'", verbose="no")

                with open(new_at, "r") as new_files:
                    return FitsArray.from_paths(new_files.read().split())
