import contextlib
import shutil
import tempfile
from glob import glob
from pathlib import Path, PurePath
from typing import List

import pandas as pd

from .base_logger import logger
from .errors import (EmissionValueError, NoiseValueError, OperandValueError,
                     OperationValueError, RejectionValueError, ScaleValueError)


class Fixer:
    @classmethod
    def fitsify(cls, path: str):
        logger.info(f"fitsify started. Prameters: {path=}")

        if not (path.endswith("fit") or path.endswith("fits")):
            return f"{path}.fits"

        return path

    @classmethod
    def nonify(cls, value: str):
        logger.info(f"nonify started. Prameters: {value=}")

        if value is None:
            return "none"

        return value

    @classmethod
    def output(
        cls,
        value: str,
        override: bool = False,
        delete: bool = True,
        prefix: str = "piron_",
        suffix: str = ".fits",
    ):
        logger.info(
            f"output started. Prameters: {value=}, {override=}, {delete=}, {prefix=}, {suffix=}"
        )

        if value is None:
            value = tempfile.NamedTemporaryFile(
                delete=delete, prefix=prefix, suffix=suffix
            ).name

        value = cls.fitsify(value)

        if Path(value).exists():
            if override:
                Path(value).unlink()
            else:
                raise FileExistsError("File already exist")
        return value

    @classmethod
    @contextlib.contextmanager
    def to_new_directory(cls, output, fits_array):
        logger.info(
            f"to_new_directory started. Prameters: {output=}, {fits_array=}")

        if output is None or not Path(output).is_dir():
            output = tempfile.mkdtemp(prefix="piron_")

        with tempfile.NamedTemporaryFile(
            delete=True, prefix="piron_", suffix=".fls", mode="w"
        ) as new_files_file:
            to_write = []
            for each_file in fits_array:
                f = each_file.path
                to_write.append(str(PurePath(output, f.name)))
            new_files_file.write("\n".join(to_write))
            new_files_file.flush()

            yield new_files_file.name

    @classmethod
    @contextlib.contextmanager
    def at_file_from_list(cls, data):
        logger.info(f"at_file_from_list started. Prameters: {data=}")

        with tempfile.NamedTemporaryFile(
            delete=True, prefix="piron_", suffix=".fls", mode="w"
        ) as new_files_file:
            new_files_file.write("\n".join(map(str, data)))
            new_files_file.flush()

            yield new_files_file.name

    @classmethod
    def yesnoify(cls, value):
        logger.info(f"yesnoify started. Prameters: {value=}")

        return "yes" if value else "no"

    @classmethod
    def iraf_coords(cls, points: pd.DataFrame):
        logger.info(f"iraf_coords started. Prameters: {points=}")

        file_name = tempfile.NamedTemporaryFile(
            delete=False, prefix="piron_", suffix=".coo"
        ).name
        points[["xcentroid", "ycentroid"]].to_csv(
            file_name, sep=" ", header=False, index=False
        )
        return file_name

    @classmethod
    def list_to_source(cls, sources: List[List[float]]) -> pd.DataFrame:
        logger.info(f"list_to_source started. Prameters: {sources=}")

        return pd.DataFrame(sources, columns=["xcentroid", "ycentroid"])

    @classmethod
    def lists_to_source(cls, xs: List[float], ys: List[float]) -> pd.DataFrame:
        return pd.DataFrame({"xcentroid": xs, "ycentroid": ys})

    @classmethod
    def tmp_cleaner(cls):
        for path in glob("/tmp/piron*"):
            if Path(path).is_file():
                Path(path).unlink()
            else:
                shutil.rmtree(path)


class Check:
    @classmethod
    def emision(cls, value: str):
        logger.info(f"emision checking. Prameters: {value=}")

        if not value.lower() in ["yes", "no"]:
            raise EmissionValueError(
                "Emision value can only be one of: yes|no")

    @classmethod
    def noise(cls, value: str):
        logger.info(f"noise checking. Prameters: {value=}")

        if not value.lower() in ["poisson", "constant"]:
            raise NoiseValueError(
                "Noise value can only be one of: poisson|constant")

    @classmethod
    def operation(cls, value: str):
        logger.info(f"operation checking. Prameters: {value=}")

        if value not in ["average", "median"]:
            raise OperationValueError(
                "Operation value can only be one of: average|median"
            )

    @classmethod
    def rejection(cls, value: str):
        logger.info(f"rejection checking. Prameters: {value=}")

        if value not in [
            "none",
            "minmax",
            "ccdclip",
            "crreject",
            "sigclip",
            "avsigclip",
            "pclip",
            None,
        ]:
            raise RejectionValueError(
                "Rejection value can only be one of: none|minmax|ccdclip|crreject|sigclip|avsigclip|pclip"
            )

    @classmethod
    def operand(cls, value: str):
        logger.info(f"operand checking. Prameters: {value=}")

        if value not in ["+", "-", "*", "/"]:
            raise OperandValueError(
                "Operand value can only be one of: +|-|*|/")

    @classmethod
    def scale(cls, value: str):
        logger.info(f"scale checking. Prameters: {value=}")

        if value not in ["none", "mode", "median", "mean", "exposure", None]:
            raise ScaleValueError(
                "Scale value can only be one of: none|mode|median|mean|exposure"
            )

    @classmethod
    def is_none(cls, value: str):
        logger.info(f"is_none checking. Prameters: {value=}")

        return value is None or value.lower() == "none"
