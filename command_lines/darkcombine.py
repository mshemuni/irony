from typing import List


def dark(files: List[str], output: str, override: bool, ope: str, rej: str, discrete: str, scale: str) -> None:
    """
    darkcombine -- Combine and process dark count images

    :param files: darkcombine -- Combine and process dark count images.
    :param output: Output dark count root image name.
    :param override: Clobber existing output images?
    :param ope: Type  of  combining  operation  performed  on  the  final set of pixels  (after  rejection).
    :param rej: Type of rejection operation.
    :param discrete: Combine images by exptime parameter? If True then the input images are grouped.
    :param scale: Multiplicative image scaling to be  applied.
    :return: None
    """
    from piron import FitsArray, Combine
    from piron.errors import ImageCountError
    from pathlib import Path

    if isinstance(files, str):
        files = [files]

    if "AVERAGE".startswith(ope.upper()):
        ope = "average"
    else:
        ope = "median"

    if "MINMAX".startswith(rej.upper()):
        rej = "minmax"
    elif "CCDLIP".startswith(rej.upper()):
        rej = "ccdclip"
    elif "CRREJECT".startswith(rej.upper()):
        rej = "crreject"
    elif "SIGRECT".startswith(rej.upper()):
        rej = "sigclip"
    elif "SIGCLIP".startswith(rej.upper()):
        rej = "sigclip"
    elif "AVGSIGCLIP".startswith(rej.upper()):
        rej = "avsigclip"
    elif "PCLIP".startswith(rej.upper()):
        rej = "pclip"
    else:
        rej = "none"

    if "MODE".startswith(scale.upper()):
        scale = "mode"
    elif "MEDIAN".startswith(scale.upper()):
        scale = "median"
    elif "MEAN".startswith(scale.upper()):
        scale = "mean"
    elif "EXPOSURE".startswith(scale.upper()):
        scale = "exposure"
    else:
        scale = "none"

    fa = FitsArray.from_paths(files)

    if discrete is not None:
        for g, img in fa.groupby(discrete).items():
            try:
                out_path = Path(output).absolute()
                out_path = str(Path(f"{str(out_path.parent)}/{str(out_path.stem)}_{g}{out_path.suffix}").absolute())
                co = Combine(img)
                co.darkcombine(ope, output=out_path, override=override, reject=rej, scale=scale)
            except ImageCountError:
                print(f"Image count for {discrete}={g} is not enough. Skipping...")
    else:
        co = Combine(fa)
        _ = co.darkcombine(ope, output=output, override=override, reject=rej, scale=scale)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog='darkcombine',
        description='Does iraf darkcombine')
    parser.add_argument('filename', nargs='*', help="file path/pattern")
    parser.add_argument('output', help="output file path")
    parser.add_argument('-f', '--force', help="overwrite if output file exist", default=False, action='store_true')
    parser.add_argument('-o', '--operation', help="combine operation. average|median", default="average")
    parser.add_argument('-r', '--rejection',
                        help="rejection operation. 'none|minmax|ccdclip|crreject|sigclip|avsigclip|pclip",
                        default="minmax")
    parser.add_argument('-d', '--discrete', help="discrete darks by exposure", default=None)
    parser.add_argument('-s', '--scale', help="Scale the combination. 'none|mode|median|mean|exposure",
                        default="seperate")

    args = parser.parse_args()
    dark(args.filename, args.output, args.force, args.operation, args.rejection, args.discrete, args.scale)


if __name__ == "__main__":
    """
    IRAF darkcombine simplified
    """
    main()
