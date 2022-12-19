from typing import List


def zero(files: List[str], output: str, override: bool, ope: str, rej: str) -> None:
    """
    zerocombine -- Combine and process zero level images

    :param files: List of zero level images to  combine.
    :param output: Output zero level root image name.
    :param override: Clobber existing output images?
    :param ope:Type of combining  operation  performed  on  the  final  set  of pixels   (after   rejection).
    :param rej: Type of rejection operation.
    :return: None
    """
    from src.irony import FitsArray, Combine


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

    fa = FitsArray.from_paths(files)
    co = Combine(fa)
    _ = co.zerocombine(ope, output=output, override=override, reject=rej)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog='zerocombine',
        description='Does iraf zerocombine')
    parser.add_argument('filename', nargs='*', help="file path/pattern")
    parser.add_argument('output', help="output file path")
    parser.add_argument('-f', '--force', help="overwrite if output file exist", default=False, action='store_true')
    parser.add_argument('-o', '--operation', help="combine operation. average|median", default="average")
    parser.add_argument('-r', '--rejection',
                        help="rejection operation. 'none|minmax|ccdclip|crreject|sigclip|avsigclip|pclip",
                        default="minmax")

    args = parser.parse_args()
    zero(args.filename, args.output, args.force, args.operation, args.rejection)


if __name__ == "__main__":
    """
    IRAF zerocombine simplified
    """
    main()
