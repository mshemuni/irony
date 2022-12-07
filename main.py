from piron import Fits

fits = Fits.from_path(r"/mnt/c/Users/mshem/OneDrive/Belgeler/iron_dont_touch/data/Bias-005.fit")
print(fits.coordinate_picker())
