from typing import List


def ccdproc(files: List[str], output: str, zero: str, dark: str, flat: str) -> None:
    """
    ccdproc -- Process CCD images

    :param files: List of input CCD images to process.
    :param output: List of output images or output directory.
    :param zero: Zero level calibration image.
    :param dark: Dark count calibration image.
    :param flat: Flat field calibration images.
    :return: None
    """
    from piron.errors import NothingToDoError
    from piron import Calibration, Fits, FitsArray
    from pathlib import Path

    if not Path(output).is_dir():
        FileNotFoundError(f"{output} does not exist")

    images = FitsArray.from_paths(files)
    zero = zero if zero is None else Fits.from_path(zero)
    dark = dark if dark is None else Fits.from_path(dark)
    flat = flat if flat is None else Fits.from_path(flat)

    try:
        ca = Calibration(images)
        _ = ca.calibrate(zero=zero, dark=dark, flat=flat, output=output)
    except NothingToDoError:
        raise NothingToDoError("No calibration file was provided")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog='darkcombine',
        description='Does iraf darkcombine')
    parser.add_argument('filename', nargs='*', help="file path/pattern")
    parser.add_argument('output', help="output file path")
    parser.add_argument('-z', '--zero', help="Master zero file", default=None)
    parser.add_argument('-d', '--dark', help="Master dark file", default=None)
    parser.add_argument('-f', '--flat', help="Master flat file", default=None)

    args = parser.parse_args()
    ccdproc(args.filename, args.output, args.zero, args.dark, args.flat)


if __name__ == "__main__":
    """
    IRAF ccdproc simplified
    """
    main()
