Usage
=====

`irony` is an easy to use package. There are two fundamental objects.

* `Fits`
* `FitsArray`


Fits
----
`Fits` is an object designed for fits files. `Fits` accepts a fits file's path as a `pathlib.Path`.


.. code-block:: python

   from irony import Fits
   from pathlib import Path

   fits = Fits(Path("Path-To-File"))

One can create a `Fits` object using an `str` as path.

.. code-block:: python

   from irony import Fits

   fits = Fits.from_path("Path-To-File")

Notice, the `Path-To-File` must exist.

header
~~~~~~

Get header of an image using `header`.

.. code-block:: python

   from irony import Fits

   fits = Fits.from_path("Path-To-File")
   fits.header

data
~~~~

Get data of an image using `data`.

.. code-block:: python

   from irony import Fits

   fits = Fits.from_path("Path-To-File")
   fits.imstat


FitsArray
---------
`FitsArray` is an object designed for fits file arrays. `FitsArray` accepts a `list` of `Fits`.

.. code-block:: python

   from irony import Fits, FitsArray
   from pathlib import Path

   fa = FitsArray([Fits(Path("Path-To-File")), Fits(Path("Path-To-File2"))])

One can create a `FitsArray` object using a `list` of `str`.

.. code-block:: python

   from irony import FitsArray

   fa = FitsArray.from_paths(["Path-To-File", "Path-To-File2"])

One can create a `FitsArray` object using patterns.

.. code-block:: python

   from irony import FitsArray

   fa = FitsArray.from_pattern(["Path-*"])

Combine
-------
`Combine` is an object designed to combine fits files. `Combine` accepts a `FitsArray`.

.. code-block:: python

   from irony import FitsArray, Combine

   fa = FitsArray.from_pattern(["Path-*"])
   com = Combine(fa)
   master_zero = com.zerocombine("median")

With the same logic one can, `combine`, `darkcombine`, `flatcombine` or `imsum` the fits files.

Calibration
-----------
`Calibration` is an object do calibration. `Calibration` accepts a `FitsArray`.

.. code-block:: python

   from irony import FitsArray, Calibration

   zeros = FitsArray.from_pattern(["Zeros-*"])
   master_zero = zeros.zerocombine("median")

   darks = FitsArray.from_pattern(["Darks-*"])
   master_dark = zeros.darkcombine("median")

   flats = FitsArray.from_pattern(["Flats-*"])
   master_flat = zeros.flatcombine("median")

   fa = FitsArray.from_pattern(["Path-*"])
   cal = Calibration(fa)
   calibrated_fits = cal.calibrate("median", zero=master_zero, dark=master_dark, flat=master_flat)

Align
-----
One can align fits images using either `Fits` or `FitsArray`

Fits
~~~~

Align a single fits file by another (reference)

.. code-block:: python

   from irony import Fits

   fits1 = Fits.from_path("Path-To-File")
   fits2 = Fits.from_path("Path-To-File2")

   aligned = fits2.align(fits1)

FitsArray
~~~~~~~~~

Align a list of fits file by another (reference). In this example first file.

.. code-block:: python

   from irony import FitsArray

   fa = FitsArray.from_pattern(["Path-*"])

   aligned = fa.align(fa[0])

This code aligns FitsArray with first fits being the reference.

APhot
-----
`APhot` is an object do photometry. `APhot` accepts a `FitsArray`.

sep
~~~

Photometry using `sep.sum_circle`.

.. code-block:: python

   from irony import FitsArray, APhot

   fa = FitsArray.from_pattern(["Path-*"])

   sources = fa[0].daofind() # or fa[0].extract()
   radius = 10
   headers_to_be_Extracted = ["JD", "ARIMASS", "FILTER"]

   aphot = APhot(fa)
   photometry = aphot.sep(sources, radius, extract=headers_to_be_Extracted)


photutils
~~~~~~~~~

Photometry using `photutils.aperture`.

.. code-block:: python

   from irony import FitsArray, APhot

   fa = FitsArray.from_pattern(["Path-*"])

   sources = fa[0].daofind() # or fa[0].extract()
   radius_inner = 10
   radius_outer = 15

   headers_to_be_Extracted = ["JD", "ARIMASS", "FILTER"]

   aphot = APhot(fa)
   photometry = aphot.photutils(sources, radius, radius_out=radius_outer, extract=headers_to_be_Extracted)

iraf
~~~~

Photometry using `iraf.digiphot.apphot.phot`.

.. code-block:: python

   from irony import FitsArray, APhot

   fa = FitsArray.from_pattern(["Path-*"])

   sources = fa[0].daofind() # or fa[0].extract()
   aperture = 10
   annulus = 15
   dannulus = 25

   headers_to_be_Extracted = ["JD", "ARIMASS", "FILTER"]

   aphot = APhot(fa)
   photometry = aphot.photutils(sources, aperture, annulus, dannulus, extract=headers_to_be_Extracted)

