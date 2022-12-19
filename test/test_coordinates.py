import pytest

from src.irony import Coordinates

DELTA = 10**-6

def test_location_from_name():
    site = Coordinates.location_from_name("TUG")
    assert site.lat.deg == pytest.approx(36.824167)
    assert site.lon.deg == pytest.approx(30.335556)

def test_location():
    site = Coordinates.location(45, 45, 2500)
    assert site.lat.deg == pytest.approx(45)
    assert site.lon.deg == pytest.approx(45)
    assert site.height.value == pytest.approx(2500)


def test_position_from_name():
    xy_leo = Coordinates.position_from_name("XY Leo")
    assert xy_leo.ra.hourangle == pytest.approx(10.027894)
    assert xy_leo.dec.deg == pytest.approx(17.409056)


def test_position():
    obj = Coordinates.position(10, 10)
    assert obj.ra.hourangle == pytest.approx(10)
    assert obj.dec.deg == pytest.approx(10)
