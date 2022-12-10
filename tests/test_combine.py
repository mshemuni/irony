import unittest

import numpy as np

from irony import Combine, FitsArray


class TestCombine(unittest.TestCase):

    def test_combine(self):
        fa = FitsArray.from_pattern("test/*.fit")

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
        np.testing.assert_equal(
            np.sum([fa[0].data, fa[1].data], axis=0), the_sum.data
        )


if __name__ == '__main__':
    unittest.main()
