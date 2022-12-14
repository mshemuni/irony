import pytest


from irony import APhot, FitsArray, Fixer

FILES = "test/files/test1.fits"
SOURCES = Fixer.list_to_source([[1495.226807, 1398.818519]])
APE = 10
ANN = 15
DAN = 20
EXPECTED_IRAF = [11.556, 0.005]
EXPECTED_SEP = [13.52960, 0.0]
EXPECTED_PHU = [13.58870, 4.470867]


def test_sep():
    fa = FitsArray.from_pattern(FILES)
    aphot = APhot(fa)
    phot = aphot.sep(SOURCES, APE)
    for calc, obs in zip(phot[["mag", "merr"]].to_numpy().tolist()[0], EXPECTED_SEP):
        assert calc == pytest.approx(obs)


def test_photutils():
    fa = FitsArray.from_pattern(FILES)
    aphot = APhot(fa)

    phot = aphot.photutils(SOURCES, APE, ANN)
    for calc, obs in zip(phot[["mag", "merr"]].to_numpy().tolist()[0], EXPECTED_PHU):
        assert calc == pytest.approx(obs)


def test_iraf():
    fa = FitsArray.from_pattern(FILES)
    aphot = APhot(fa)

    phot = aphot.iraf(SOURCES, APE, ANN, DAN)
    for calc, obs in zip(phot["mag"].to_numpy().tolist(), EXPECTED_IRAF):
        assert calc == pytest.approx(obs)
