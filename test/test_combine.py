import numpy as np

from src.irony import Combine, FitsArray


def test_combine():
    fa = FitsArray.from_pattern("test/files/test*.fits")

    c = Combine(fa)

    median = c.combine("median")
    np.testing.assert_equal(
        np.median([fa[0].data, fa[1].data], axis=0), median.data
    )

    average = c.combine("average")
    np.testing.assert_equal(
        np.mean([fa[0].data, fa[1].data], axis=0), average.data
    )

    the_sum = c.imsum()
    # Interesting. IRAF does modulo operation on imsum? -_-
    np.testing.assert_equal(
        np.sum([fa[0].data, fa[1].data], axis=0) % 65536, the_sum.data
    )
