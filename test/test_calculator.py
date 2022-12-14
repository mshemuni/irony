import pytest

from irony import Calculator, Coordinates, FitsArray

FILES = "test/files/test*.fits"


def test_jd_c():
    fa = FitsArray.from_pattern(FILES)
    dates = fa.hselect("DATE-OBS").to_numpy().flatten().tolist()
    jds = Calculator.jd_c(dates).to_numpy().flatten().tolist()
    assert jds == pytest.approx([2456865.423257292, 2456865.421439815])


def test_sec_z_c():
    site = Coordinates.location(45, 45, 2000)
    v523_cas = Coordinates.position_from_name("v523 Cas")
    fa = FitsArray.from_pattern(FILES)
    dates = fa.hselect("DATE-OBS").to_numpy().flatten().tolist()
    secz = Calculator.sec_z_c(
        dates, site, v523_cas
    ).to_numpy().flatten().tolist()
    assert secz == pytest.approx([1.1844316720852472, 1.1899036959879108])
