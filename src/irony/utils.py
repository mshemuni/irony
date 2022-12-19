from __future__ import annotations
import contextlib
import shutil
import tempfile
from glob import glob
from pathlib import Path, PurePath
from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fits import FitsArray

import pandas as pd

from .base_logger import logger
from .errors import (EmissionValueError, NoiseValueError, OperandValueError,
                     OperationValueError, RejectionValueError, ScaleValueError)


class Fixer:
    @classmethod
    def fitsify(cls, path: str) -> str:
        """
        Makes sure a file name ends either with fit or fits

        Parameters
        ----------
        path: str
            Path of the file

        Returns
        -------
        str
            New path
        """
        logger.info(f"fitsify started. Parameters: {path=}")

        if not (path.endswith("fit") or path.endswith("fits")):
            return f"{path}.fits"

        return path

    @classmethod
    def nonify(cls, value: str) -> str:
        """
        Converts None to "none"

        Parameters
        ----------
        value: str
            Any value

        Returns
        -------
        str
            new value
        """
        logger.info(f"nonify started. Parameters: {value=}")

        if value is None:
            return "none"

        return value

    @classmethod
    def output(cls, value: str, override: bool = False, delete: bool = True, prefix: str = "irony_", suffix: str = ".fits") -> str:
        """

        Parameters
        ----------
        value: str
        override: bool
        delete: bool
        prefix: str
        suffix: str

        Returns
        -------
        str
        """
        logger.info(f"output started. Parameters: {value=}, {override=}, {delete=}, {prefix=}, {suffix=}")

        if value is None:
            value = tempfile.NamedTemporaryFile(delete=delete, prefix=prefix, suffix=suffix).name

        value = cls.fitsify(value)

        if Path(value).exists():
            if override:
                Path(value).unlink()
            else:
                raise FileExistsError("File already exist")
        return value

    @classmethod
    @contextlib.contextmanager
    def to_new_directory(cls, output: str, fits_array: FitsArray) -> str:
        """

        Parameters
        ----------
        output: str
        fits_array: FitsArray

        Returns
        -------
        ste
        """
        logger.info(f"to_new_directory started. Parameters: {output=}, {fits_array=}")

        if output is None or not Path(output).is_dir():
            output = tempfile.mkdtemp(prefix="irony_")

        with tempfile.NamedTemporaryFile(delete=True, prefix="irony_", suffix=".fls", mode="w") as new_files_file:
            to_write = []
            for each_file in fits_array:
                f = each_file.path
                to_write.append(str(PurePath(output, f.name)))
            new_files_file.write("\n".join(to_write))
            new_files_file.flush()

            yield new_files_file.name

    @classmethod
    @contextlib.contextmanager
    def at_file_from_list(cls, data) -> str:
        """

        Parameters
        ----------
        data: list

        Returns
        -------
        str
        """
        logger.info(f"at_file_from_list started. Parameters: {data=}")

        with tempfile.NamedTemporaryFile(delete=True, prefix="irony_", suffix=".fls", mode="w") as new_files_file:
            new_files_file.write("\n".join(map(str, data)))
            new_files_file.flush()

            yield new_files_file.name

    @classmethod
    def yesnoify(cls, value: str) -> str:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        str
        """
        logger.info(f"yesnoify started. Parameters: {value=}")

        return "yes" if value else "no"

    @classmethod
    @contextlib.contextmanager
    def iraf_coords(cls, points: pd.DataFrame) -> str:
        """

        Parameters
        ----------
        points: pd.DataFrame

        Returns
        -------
        str
        """
        logger.info(f"iraf_coords started. Parameters: {points=}")
        with tempfile.NamedTemporaryFile(delete=True, prefix="irony_", suffix=".coo", mode="w") as new_files_file:
            # file_name = tempfile.NamedTemporaryFile(delete=False, prefix="irony_", suffix=".coo").name
            points[["xcentroid", "ycentroid"]].to_csv(new_files_file.name, sep=" ", header=False, index=False)
            new_files_file.flush()
            yield new_files_file.name

    @classmethod
    def list_to_source(cls, sources: List[List[float]]) -> pd.DataFrame:
        """

        Parameters
        ----------
        sources: List[List[float]]

        Returns
        -------
        pd.DataFrame
        """
        logger.info(f"list_to_source started. Parameters: {sources=}")

        return pd.DataFrame(sources, columns=["xcentroid", "ycentroid"])

    @classmethod
    def lists_to_source(cls, xs: List[float], ys: List[float]) -> pd.DataFrame:
        """

        Parameters
        ----------
        xs: List[float]
        ys: List[float]

        Returns
        -------
        pd.DataFrame
        """
        return pd.DataFrame({"xcentroid": xs, "ycentroid": ys})

    @classmethod
    def tmp_cleaner(cls):
        """
        Cleans tem folder
        Returns
        -------

        """
        for path in glob("/tmp/irony*"):
            if Path(path).is_file():
                Path(path).unlink()
            else:
                shutil.rmtree(path)


class Check:
    @classmethod
    def emision(cls, value: str) -> None:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        None
            None.
        """
        logger.info(f"emision checking. Parameters: {value=}")

        if not value.lower() in ["yes", "no"]:
            raise EmissionValueError("Emision value can only be one of: yes|no")

    @classmethod
    def noise(cls, value: str) -> None:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        None
            None.
        """
        logger.info(f"noise checking. Parameters: {value=}")

        if not value.lower() in ["poisson", "constant"]:
            raise NoiseValueError("Noise value can only be one of: poisson|constant")

    @classmethod
    def operation(cls, value: str) -> None:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        None
            None.
        """
        logger.info(f"operation checking. Parameters: {value=}")

        if value not in ["average", "median"]:
            raise OperationValueError("Operation value can only be one of: average|median")

    @classmethod
    def rejection(cls, value: str) -> None:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        None
            None.
        """
        logger.info(f"rejection checking. Parameters: {value=}")

        if value not in [ "none", "minmax", "ccdclip", "crreject", "sigclip", "avsigclip", "pclip", None]:
            raise RejectionValueError("Rejection value can only be one of: none|minmax|ccdclip|crreject|sigclip|avsigclip|pclip")

    @classmethod
    def operand(cls, value: str) -> None:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        None
            None.
        """
        logger.info(f"operand checking. Parameters: {value=}")

        if value not in ["+", "-", "*", "/"]:
            raise OperandValueError("Operand value can only be one of: +|-|*|/")

    @classmethod
    def scale(cls, value: str) -> None:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        None
            None.
        """
        logger.info(f"scale checking. Parameters: {value=}")

        if value not in ["none", "mode", "median", "mean", "exposure", None]:
            raise ScaleValueError("Scale value can only be one of: none|mode|median|mean|exposure")

    @classmethod
    def is_none(cls, value: str) -> str:
        """

        Parameters
        ----------
        value: str

        Returns
        -------
        str
        """
        logger.info(f"is_none checking. Parameters: {value=}")

        return value is None or value.lower() == "none"
