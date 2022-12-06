import unittest

from piron import Calculator, Coordinates, FitsArray


class TestCalculator(unittest.TestCase):

    def test_jd_c(self):
        fa = FitsArray.from_pattern("test/test*.fit")
        dates = fa.hselect("DATE-OBS").to_numpy().flatten().tolist()
        jds = Calculator.jd_c(dates).to_numpy().flatten().tolist()
        for calc, obs in zip(jds, [2456579.61890, 2456579.60028]):
            self.failIfAlmostEqual(calc, obs, delta=10**-3)

    def test_sec_z_c(self):
        site = Coordinates.location(45, 45, 2000)
        v523_cas = Coordinates.position_from_name("v523 Cas")
        fa = FitsArray.from_pattern("test/test*.fit")
        dates = fa.hselect("DATE-OBS").to_numpy().flatten().tolist()
        secz = Calculator.sec_z_c(
            dates, site, v523_cas
            ).to_numpy().flatten().tolist()

        for calc, obs in zip(secz, [1.44413045019, 1.34886337532]):
            self.failIfAlmostEqual(calc, obs, delta=10**-13)


if __name__ == '__main__':
    unittest.main()
