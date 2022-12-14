from irony import FitsArray, Combine, Calibration, \
    Calculator, Coordinates, APhot

# Get all images available in directory
fa = FitsArray.from_pattern("path*")

# Group images by `IMAGETYP`. Zero, Dark, Flat and Images
grouped = fa.groupby("IMAGETYP")

zeros = grouped["Bias Frame"]
darks = grouped["Dark Frame"]
flats = grouped["Flat Field"]
images = grouped["Light Frame"]

# Create a combiner to do zerocombine
z_combine = Combine(zeros)
master_zero = z_combine.zerocombine("median")


# Group, darks, flats and images
dark_group = darks.groupby("EXPTIME")
flat_group = flats.groupby("FILTER")
images_group = images.groupby(["EXPTIME", "FILTER"])

for (expt, fltr), img in images_group.items():
    # Create master dark for given exptime
    d_combine = Combine(dark_group[expt])
    mast_dark = d_combine.darkcombine("median")

    # Create master flat for given filter
    f_combine = Combine(flat_group[fltr])
    mast_flat = f_combine.flatcombine("median")

    # Calibrate images and save them in `cali` directory
    calibrator = Calibration(img)
    calibrator.calibrate(output="cali", zero=master_zero,
                         dark=mast_dark, flat=mast_flat)

# Get calibrated images.
calibrated = FitsArray.from_pattern("cali/*")

# Align calibrated images and save them in `ali` directory
aligned = calibrated.align(calibrated[0], output="ali")

site = Coordinates.location_from_name("Location Name")
objc = Coordinates.position_from_name("Object Name")

c = Calculator(aligned)

# Calculate and Add HJD to the header.
c.hjd("DATE-OBS", objc, new_key="HJD",
      date_format="isot", scale="utc")

# Calculate and Add AIRMASS/SECZ to the header.
c.sec_z("DATE-OBS", site, objc, new_key="AIRMASS",
        date_format="isot", scale="utc")


aphot = APhot(aligned)

# Extract source coordinates
sources = aligned[0].daofind()

# Do iraf photometry
iraf_phot = aphot.iraf(sources, 10, 15, 20,
                       extract=["HJD", "AIRMASS", "FILTER"])
