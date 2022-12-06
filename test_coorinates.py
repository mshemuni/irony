import unittest

from piron import Coordinates


class TestCoordinates(unittest.TestCase):

    DELTA = 10**-6

    def test_location_from_name(self):
        site = Coordinates.location_from_name("TUG")
        self.assertAlmostEqual(site.lat.deg, 36.824167, delta=self.DELTA)
        self.assertAlmostEqual(site.lon.deg, 30.335556, delta=self.DELTA)

    def test_location(self):
        site = Coordinates.location(45, 45, 2500)
        self.assertAlmostEqual(site.lat.deg, 45, delta=self.DELTA)
        self.assertAlmostEqual(site.lon.deg, 45, delta=self.DELTA)
        self.assertAlmostEqual(site.height.value, 2500, delta=self.DELTA)

    def test_position_from_name(self):
        xy_leo = Coordinates.position_from_name("XY Leo")
        self.assertAlmostEqual(
            xy_leo.ra.hourangle, 10.027894, delta=self.DELTA
            )
        self.assertAlmostEqual(xy_leo.dec.deg, 17.409056, delta=self.DELTA)
        self.assertEqual(1, 1)

    def test_position(self):
        xy_leo = Coordinates.position(10, 10)
        self.assertAlmostEqual(xy_leo.ra.hourangle, 10, delta=self.DELTA)
        self.assertAlmostEqual(xy_leo.dec.deg, 10, delta=self.DELTA)
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
