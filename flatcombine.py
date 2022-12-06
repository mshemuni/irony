def flat(files, output, override, ope, rej, discrete, scale):
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
        ope = "none"

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
                co.flatcombine(ope, output=out_path, override=override, reject=rej, scale=scale)
            except ImageCountError:
                print(f"Image count for {discrete}={g} is not enough. Skipping...")
    else:
        co = Combine(fa)
        co.flatcombine(ope, output=output, override=override, reject=rej, scale=scale)

def main():
    import argparse


    parser = argparse.ArgumentParser(
                    prog = 'flatcombine',
                    description = 'Does iraf flatcombine')
    parser.add_argument('filename', nargs='*', help="file path/pattern")
    parser.add_argument('output', help="output file path")
    parser.add_argument('-f', '--force', help="overwrite if output file exist", default=False, action='store_true')
    parser.add_argument('-o', '--operation', help="combine operation. average|median", default="average")
    parser.add_argument('-r', '--rejection', help="rejection operation. 'none|minmax|ccdclip|crreject|sigclip|avsigclip|pclip", default="minmax")
    parser.add_argument('-d', '--discrete', help="discrete flats by filter", default=None)
    parser.add_argument('-s', '--scale', help="Scale the combination. 'none|mode|median|mean|exposure", default="seperate")
    
    args = parser.parse_args()
    flat(args.filename, args.output, args.force, args.operation, args.rejection, args.discrete, args.scale)


if __name__ == "__main__":
    """
    IRAF flatcombine simplified
    """
    main()
