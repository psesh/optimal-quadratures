from unittest import TestCase
import unittest
from equadratures.sampling_methods.induced import Induced
from equadratures.parameter import Parameter
from equadratures.basis import Basis

import numpy as np


class TestSamplingGeneration(TestCase):

    def test_induced_jacobi_evaluation(self):

        dimension = 3
        parameters = [Parameter(3, "Uniform", upper=1, lower=-1)]*dimension
        basis = Basis("total-order", [5]*dimension)

        induced_sampling = Induced(parameters, basis)

        parameter = parameters[0]
        parameter.order = 3
        cdf_value = induced_sampling.induced_jacobi_evaluation(0, 0, 0, parameter)
        np.testing.assert_allclose(cdf_value, 0.5, atol=0.00001)
        cdf_value = induced_sampling.induced_jacobi_evaluation(0, 0, 1, parameter)
        assert cdf_value == 1
        cdf_value = induced_sampling.induced_jacobi_evaluation(0, 0, -1, parameter)
        assert cdf_value == 0
        cdf_value = induced_sampling.induced_jacobi_evaluation(0, 0, 0.6, parameter)
        np.testing.assert_allclose(cdf_value, 0.7462, atol=0.00005)
        cdf_value = induced_sampling.induced_jacobi_evaluation(0, 0, 0.999, parameter)
        np.testing.assert_allclose(cdf_value, 0.99652, atol=0.000005)

    def test_induced_sampling(self):
        """
        An integration test for the whole routine
        """
        dimension = 3
        parameters = [Parameter(3, "Uniform", upper=1, lower=-1)]*dimension
        basis = Basis("total-order", [3]*dimension)

        induced_sampling = Induced(parameters, basis)

        quadrature_points = induced_sampling.get_points()
        assert quadrature_points.shape == (63, 3)


if __name__ == '__main__':
    unittest.main()
