import unittest

from irony import APhot, FitsArray, Fixer


class TestPhotometry(unittest.TestCase):

    SOURCES = Fixer.list_to_source([[1107, 968], [626, 593]])
    APE = 10
    ANN = 15
    DAN = 25
    EXPECTED = [11.147, 11.148]

    def test_sep(self):
        fa = FitsArray.from_pattern("test/test.fit")
        aphot = APhot(fa)
        phot = aphot.sep(self.SOURCES, self.APE)
        for calc, obs in (phot["mag"].to_numpy().tolist(), self.EXPECTED):
            self.assertAlmostEqual(calc, obs, delta=10**-1)

    def test_sep(self):
        fa = FitsArray.from_pattern("test/test.fit")
        aphot = APhot(fa)

        phot = aphot.sep(self.SOURCES, self.APE)
        for calc, obs in (phot["mag"].to_numpy().tolist(), self.EXPECTED):
            self.assertAlmostEqual(calc, obs, delta=10**-1)

    def test_photutils(self):
        fa = FitsArray.from_pattern("test/test.fit")
        aphot = APhot(fa)

        phot = aphot.photutils(self.SOURCES, self.APE, self.ANN)
        for calc, obs in (phot["mag"].to_numpy().tolist(), self.EXPECTED):
            self.assertAlmostEqual(calc, obs, delta=10**-1)

    def test_photutils(self):
        fa = FitsArray.from_pattern("test/test.fit")
        aphot = APhot(fa)

        phot = aphot.iraf(self.SOURCES, self.APE, self.ANN, self.DAN)
        for calc, obs in zip(phot["mag"].to_numpy().tolist(), [20.0, 19.5]):
            self.assertAlmostEqual(calc, obs, delta=10**-1)


if __name__ == '__main__':
    unittest.main()
