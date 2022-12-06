import optparse


def main():
    parser = optparse.OptionParser()
    parser.add_option('-a', '--action', dest='action',
                      help='The action. `zerocombine`, `darkcombine`, `flatcombine`, `calibration`, `align`, `phptometry`')

    parser.add_option('-z', '--zero', dest='zeros', default=None,
            help='zero file(s)')

    parser.add_option('-d', '--dark', dest='darks', default=None,
            help='dark file(s)')

    parser.add_option('-d', '--flat', dest='flats', default=None,
            help='flat file(s)')

    parser.add_option('-i' '--images', dest='Images', default=None,
            help='Lis of images')

    parser.add_option('-r', '--reference', dest='Reference', default=None,
            help='Reference Image for align')

    parser.add_option('-s', '--sources', dest='Sources', default=None,
            help='List of sources')

    parser.add_option('-ap', '--aperture', dest='Aperture', default=None,
            help='Aperture of the photometry')

    parser.add_option('-ann', '--annulus', dest='Annulus', default=None,
            help='Annulus of the photometry')

    parser.add_option('-dan', '--dannulus', dest='Dannulus', default=None,
            help='Dannulus of the photometry')

        

if __name__ == "__main__":
    pass