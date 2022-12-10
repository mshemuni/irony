# from astroquery.astrometry_net import AstrometryNet
#
# ast = AstrometryNet()
#
# ast.api_key = 'khxbtvvxvejbxozn'
# # print(ast.key)
#
# wcs_header = ast.solve_from_image('data/V523_Cas-004V.fit', force_image_upload=True)
# print(wcs_header)


from piron import FitsArray, APhot, Fixer

fa = FitsArray.from_pattern("data/*.fit")
ap = APhot(fa)
s = fa[0].coordinate_picker()
if s is not None:
    phot_i = ap.iraf(s, 10, 15, 20)
    phot_s = ap.sep(s, 10)
    phot_p = ap.photutils(s, 10, 15)
    print(phot_i)
    print(phot_s)
    print(phot_p)
# f = Fits.from_path("data/V523_Cas-004V.fit")
# f.astrometry("khxbtvvxvejbxozn")
# print(f.header)
