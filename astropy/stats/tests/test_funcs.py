# Licensed under a 3-clause BSD style license - see LICENSE.rst

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from numpy.random import randn, normal
from numpy.testing import assert_equal
from numpy.testing.utils import assert_allclose

try:
    import scipy  # pylint: disable=W0611
except ImportError:
    HAS_SCIPY = False
else:
    HAS_SCIPY = True

try:
    import mpmath  # pylint: disable=W0611
except ImportError:
    HAS_MPMATH = False
else:
    HAS_MPMATH = True

from ...tests.helper import pytest

from .. import funcs

# These are not part of __all__ because they are just the lower level versions
# of poisson_upper_limit
# from ..funcs import scipy_poisson_upper_limit, mpmath_poisson_upper_limit

from ...utils.misc import NumpyRNGContext
from ... import units as u


def test_median_absolute_deviation():
    # need to seed the numpy RNG to make sure we don't get some amazingly
    # flukey random number that breaks one of the tests

    with NumpyRNGContext(12345):

        # test that it runs
        randvar = randn(10000)
        mad = funcs.median_absolute_deviation(randvar)

        # test whether an array is returned if an axis is used
        randvar = randvar.reshape((10, 1000))
        mad = funcs.median_absolute_deviation(randvar, axis=1)
        assert len(mad) == 10
        assert mad.size < randvar.size
        mad = funcs.median_absolute_deviation(randvar, axis=0)
        assert len(mad) == 1000
        assert mad.size < randvar.size
        # Test some actual values in a 3 dimensional array
        x = np.arange(3*4*5)
        a = np.array([sum(x[:i+1]) for i in range(len(x))]).reshape(3, 4, 5)
        mad = funcs.median_absolute_deviation(a)
        assert mad == 389.5
        mad = funcs.median_absolute_deviation(a, axis=0)
        assert_allclose(mad, [[210.,  230.,  250.,  270.,  290.],
                              [310.,  330.,  350.,  370.,  390.],
                              [410.,  430.,  450.,  470.,  490.],
                              [510.,  530.,  550.,  570.,  590.]])
        mad = funcs.median_absolute_deviation(a, axis=1)
        assert_allclose(mad, [[27.5,   32.5,   37.5,   42.5,   47.5],
                              [127.5,  132.5,  137.5,  142.5,  147.5],
                              [227.5,  232.5,  237.5,  242.5,  247.5]])
        mad = funcs.median_absolute_deviation(a, axis=2)
        assert_allclose(mad, [[3.,   8.,  13.,  18.],
                              [23.,  28.,  33.,  38.],
                              [43.,  48.,  53.,  58.]])


def test_median_absolute_deviation_masked():
    # Based on the changes introduces in #4658

    # normal masked arrays without masked values are handled like normal
    # numpy arrays
    array = np.ma.array([1, 2, 3])
    assert funcs.median_absolute_deviation(array) == 1

    # masked numpy arrays return something different (rank 0 masked array)
    # but one can still compare it without np.all!
    array = np.ma.array([1, 4, 3], mask=[0, 1, 0])
    assert funcs.median_absolute_deviation(array) == 1
    # Just cross check if that's identical to the function on the unmasked
    # values only
    assert funcs.median_absolute_deviation(array) == (
            funcs.median_absolute_deviation(array[~array.mask]))

    # Multidimensional masked array
    array = np.ma.array([[1, 4], [2, 2]], mask=[[1, 0], [0, 0]])
    funcs.median_absolute_deviation(array)
    assert funcs.median_absolute_deviation(array) == 0
    # Just to compare it with the data without mask:
    assert funcs.median_absolute_deviation(array.data) == 0.5

    # And check if they are also broadcasted correctly
    np.testing.assert_array_equal(
        funcs.median_absolute_deviation(array, axis=0).data, [0, 1])
    np.testing.assert_array_equal(
        funcs.median_absolute_deviation(array, axis=1).data, [0, 0])


def test_median_absolute_deviation_quantity():
    # Based on the changes introduces in #4658

    # Just a small test that this function accepts Quantities and returns a
    # quantity
    a = np.array([1, 16, 5]) * u.m
    mad = funcs.median_absolute_deviation(a)
    # Check for the correct unit and that the result is identical to the result
    # without units.
    assert mad.unit == a.unit
    assert mad.value == funcs.median_absolute_deviation(a.value)


def test_biweight_location():
    # need to seed the numpy RNG to make sure we don't get some
    # amazingly flukey random number that breaks one of the tests

    with NumpyRNGContext(12345):

        # test that it runs
        randvar = randn(10000)
        cbl = funcs.biweight_location(randvar)

        assert abs(cbl-0) < 1e-2


def test_biweight_location_small():

    cbl = funcs.biweight_location([1, 3, 5, 500, 2])
    assert abs(cbl-2.745) < 1e-3


def test_biweight_location_axis():
    """Test a 2D array with the axis keyword."""
    with NumpyRNGContext(12345):
        ny = 100
        nx = 200
        data = normal(5, 2, (ny, nx))

        bw = funcs.biweight_location(data, axis=0)
        bwi = []
        for i in range(nx):
            bwi.append(funcs.biweight_location(data[:, i]))
        bwi = np.array(bwi)
        assert_allclose(bw, bwi)

        bw = funcs.biweight_location(data, axis=1)
        bwi = []
        for i in range(ny):
            bwi.append(funcs.biweight_location(data[i, :]))
        bwi = np.array(bwi)
        assert_allclose(bw, bwi)


def test_biweight_location_axis_3d():
    """Test a 3D array with the axis keyword."""
    with NumpyRNGContext(12345):
        nz = 3
        ny = 4
        nx = 5
        data = normal(5, 2, (nz, ny, nx))
        bw = funcs.biweight_location(data, axis=0)
        assert bw.shape == (ny, nx)

        y = 0
        bwi = []
        for i in range(nx):
            bwi.append(funcs.biweight_location(data[:, y, i]))
        bwi = np.array(bwi)
        assert_allclose(bw[y], bwi)


def test_biweight_midvariance():
    # need to seed the numpy RNG to make sure we don't get some
    # amazingly flukey random number that breaks one of the tests

    with NumpyRNGContext(12345):

        # test that it runs
        randvar = randn(10000)
        scl = funcs.biweight_midvariance(randvar)

        assert abs(scl-1) < 1e-2


def test_biweight_midvariance_small():
    scl = funcs.biweight_midvariance([1, 3, 5, 500, 2])
    assert abs(scl-1.529) < 1e-3


def test_biweight_midvariance_5127():
    # test a regression introduced in #5127
    rand = np.random.RandomState(12345)
    data = rand.normal(loc=0., scale=20., size=(100, 100))
    scl = funcs.biweight_midvariance(data)
    assert_allclose(scl, 20.171003621738148)    # test against previous code


def test_biweight_midvariance_axis():
    """Test a 2D array with the axis keyword."""
    with NumpyRNGContext(12345):
        ny = 100
        nx = 200
        data = normal(5, 2, (ny, nx))

        bw = funcs.biweight_midvariance(data, axis=0)
        bwi = []
        for i in range(nx):
            bwi.append(funcs.biweight_midvariance(data[:, i]))
        bwi = np.array(bwi)
        assert_allclose(bw, bwi)

        bw = funcs.biweight_midvariance(data, axis=1)
        bwi = []
        for i in range(ny):
            bwi.append(funcs.biweight_midvariance(data[i, :]))
        bwi = np.array(bwi)
        assert_allclose(bw, bwi)


def test_biweight_midvariance_axis_3d():
    """Test a 3D array with the axis keyword."""
    with NumpyRNGContext(12345):
        nz = 3
        ny = 4
        nx = 5
        data = normal(5, 2, (nz, ny, nx))
        bw = funcs.biweight_midvariance(data, axis=0)
        assert bw.shape == (ny, nx)

        y = 0
        bwi = []
        for i in range(nx):
            bwi.append(funcs.biweight_midvariance(data[:, y, i]))
        bwi = np.array(bwi)
        assert_allclose(bw[y], bwi)


@pytest.mark.skipif('not HAS_SCIPY')
def test_binom_conf_interval():

    # Test Wilson and Jeffreys interval for corner cases:
    # Corner cases: k = 0, k = n, conf = 0., conf = 1.
    n = 5
    k = [0, 4, 5]
    for conf in [0., 0.5, 1.]:
        res = funcs.binom_conf_interval(k, n, conf=conf, interval='wilson')
        assert ((res >= 0.) & (res <= 1.)).all()
        res = funcs.binom_conf_interval(k, n, conf=conf, interval='jeffreys')
        assert ((res >= 0.) & (res <= 1.)).all()

    # Test Jeffreys interval accuracy against table in Brown et al. (2001).
    # (See `binom_conf_interval` docstring for reference.)
    k = [0, 1, 2, 3, 4]
    n = 7
    conf = 0.95
    result = funcs.binom_conf_interval(k, n, conf=conf, interval='jeffreys')
    table = np.array([[0.000, 0.016, 0.065, 0.139, 0.234],
                      [0.292, 0.501, 0.648, 0.766, 0.861]])
    assert_allclose(result, table, atol=1.e-3, rtol=0.)

    # Test scalar version
    result = np.array([funcs.binom_conf_interval(kval, n, conf=conf,
                                                 interval='jeffreys')
                       for kval in k]).transpose()
    assert_allclose(result, table, atol=1.e-3, rtol=0.)

    # Test flat
    result = funcs.binom_conf_interval(k, n, conf=conf, interval='flat')
    table = np.array([[0., 0.03185, 0.08523, 0.15701, 0.24486],
                      [0.36941, 0.52650, 0.65085, 0.75513, 0.84298]])
    assert_allclose(result, table, atol=1.e-3, rtol=0.)

    # Test scalar version
    result = np.array([funcs.binom_conf_interval(kval, n, conf=conf,
                                                 interval='flat')
                       for kval in k]).transpose()
    assert_allclose(result, table, atol=1.e-3, rtol=0.)

    # Test Wald interval
    result = funcs.binom_conf_interval(0, 5, interval='wald')
    assert_allclose(result, 0.)  # conf interval is [0, 0] when k = 0
    result = funcs.binom_conf_interval(5, 5, interval='wald')
    assert_allclose(result, 1.)  # conf interval is [1, 1] when k = n
    result = funcs.binom_conf_interval(500, 1000, conf=0.68269,
                                       interval='wald')
    assert_allclose(result[0], 0.5 - 0.5 / np.sqrt(1000.))
    assert_allclose(result[1], 0.5 + 0.5 / np.sqrt(1000.))

    # Test shapes
    k = 3
    n = 7
    for interval in ['wald', 'wilson', 'jeffreys', 'flat']:
        result = funcs.binom_conf_interval(k, n, interval=interval)
        assert result.shape == (2,)

    k = np.array(k)
    for interval in ['wald', 'wilson', 'jeffreys', 'flat']:
        result = funcs.binom_conf_interval(k, n, interval=interval)
        assert result.shape == (2,)

    n = np.array(n)
    for interval in ['wald', 'wilson', 'jeffreys', 'flat']:
        result = funcs.binom_conf_interval(k, n, interval=interval)
        assert result.shape == (2,)

    k = np.array([1, 3, 5])
    for interval in ['wald', 'wilson', 'jeffreys', 'flat']:
        result = funcs.binom_conf_interval(k, n, interval=interval)
        assert result.shape == (2, 3)

    n = np.array([5, 5, 5])
    for interval in ['wald', 'wilson', 'jeffreys', 'flat']:
        result = funcs.binom_conf_interval(k, n, interval=interval)
        assert result.shape == (2, 3)


@pytest.mark.skipif('not HAS_SCIPY')
def test_binned_binom_proportion():

    # Check that it works.
    nbins = 20
    x = np.linspace(0., 10., 100)  # Guarantee an `x` in every bin.
    success = np.ones(len(x), dtype=np.bool)
    bin_ctr, bin_hw, p, perr = funcs.binned_binom_proportion(x, success,
                                                             bins=nbins)

    # Check shape of outputs
    assert bin_ctr.shape == (nbins,)
    assert bin_hw.shape == (nbins,)
    assert p.shape == (nbins,)
    assert perr.shape == (2, nbins)

    # Check that p is 1 in all bins, since success = True for all `x`.
    assert (p == 1.).all()

    # Check that p is 0 in all bins if success = False for all `x`.
    success[:] = False
    bin_ctr, bin_hw, p, perr = funcs.binned_binom_proportion(x, success,
                                                             bins=nbins)
    assert (p == 0.).all()


def test_signal_to_noise_oir_ccd():

    result = funcs.signal_to_noise_oir_ccd(1, 25, 0, 0, 0, 1)
    assert 5.0 == result
    # check to make sure gain works
    result = funcs.signal_to_noise_oir_ccd(1, 5, 0, 0, 0, 1, 5)
    assert 5.0 == result

    # now add in sky, dark current, and read noise
    # make sure the snr goes down
    result = funcs.signal_to_noise_oir_ccd(1, 25, 1, 0, 0, 1)
    assert result < 5.0
    result = funcs.signal_to_noise_oir_ccd(1, 25, 0, 1, 0, 1)
    assert result < 5.0
    result = funcs.signal_to_noise_oir_ccd(1, 25, 0, 0, 1, 1)
    assert result < 5.0

    # make sure snr increases with time
    result = funcs.signal_to_noise_oir_ccd(2, 25, 0, 0, 0, 1)
    assert result > 5.0


def test_bootstrap():
    bootarr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 0])
    # test general bootstrapping
    answer = np.array([[7, 4, 8, 5, 7, 0, 3, 7, 8, 5],
                       [4, 8, 8, 3, 6, 5, 2, 8, 6, 2]])
    with NumpyRNGContext(42):
        assert_equal(answer, funcs.bootstrap(bootarr, 2))

    # test with a bootfunction
    with NumpyRNGContext(42):
        bootresult = np.mean(funcs.bootstrap(bootarr, 10000, bootfunc=np.mean))
        assert_allclose(np.mean(bootarr), bootresult, atol=0.01)


@pytest.mark.skipif('not HAS_SCIPY')
def test_bootstrap_multiple_outputs():

    from scipy.stats import spearmanr

    # test a bootfunc with several output values
    # return just bootstrapping with one output from bootfunc
    with NumpyRNGContext(42):
        bootarr = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
                            [4, 8, 8, 3, 6, 5, 2, 8, 6, 2]]).T

        answer = np.array((0.19425, 0.02094))

        def bootfunc(x): return spearmanr(x)[0]

        bootresult = funcs.bootstrap(bootarr, 2,
                                     bootfunc=bootfunc)

        assert_allclose(answer, bootresult, atol=1e-3)

    # test a bootfunc with several output values
    # return just bootstrapping with the second output from bootfunc
    with NumpyRNGContext(42):
        bootarr = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
                            [4, 8, 8, 3, 6, 5, 2, 8, 6, 2]]).T

        answer = np.array((0.5907,
                           0.9541))

        def bootfunc(x): return spearmanr(x)[1]

        bootresult = funcs.bootstrap(bootarr, 2,
                                     bootfunc=bootfunc)

        assert_allclose(answer, bootresult, atol=1e-3)

    # return just bootstrapping with two outputs from bootfunc
    with NumpyRNGContext(42):
        answer = np.array(((0.1942, 0.5907),
                           (0.0209, 0.9541),
                           (0.4286, 0.2165)))

        def bootfunc(x): return spearmanr(x)

        bootresult = funcs.bootstrap(bootarr, 3,
                                     bootfunc=bootfunc)

        assert bootresult.shape == (3, 2)
        assert_allclose(answer, bootresult, atol=1e-3)


def test_mad_std():
    with NumpyRNGContext(12345):
        data = normal(5, 2, size=(100, 100))
        assert_allclose(funcs.mad_std(data), 2.0, rtol=0.05)


def test_mad_std_with_axis():
    data = np.array([[1, 2, 3, 4],
                     [4, 3, 2, 1]])
    # results follow data symmetry
    result_axis0 = np.array([2.22390333, 0.74130111, 0.74130111,
                             2.22390333])
    result_axis1 = np.array([1.48260222, 1.48260222])
    assert_allclose(funcs.mad_std(data, axis=0), result_axis0)
    assert_allclose(funcs.mad_std(data, axis=1), result_axis1)


def test_gaussian_fwhm_to_sigma():
    fwhm = (2.0 * np.sqrt(2.0 * np.log(2.0)))
    assert_allclose(funcs.gaussian_fwhm_to_sigma * fwhm, 1.0, rtol=1.0e-6)


def test_gaussian_sigma_to_fwhm():
    sigma = 1.0 / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    assert_allclose(funcs.gaussian_sigma_to_fwhm * sigma, 1.0, rtol=1.0e-6)


def test_gaussian_sigma_to_fwhm_to_sigma():
    assert_allclose(funcs.gaussian_fwhm_to_sigma *
                    funcs.gaussian_sigma_to_fwhm, 1.0)


def test_poisson_conf_interval_rootn():
    assert_allclose(funcs.poisson_conf_interval(16, interval='root-n'),
                    (12, 20))


@pytest.mark.skipif('not HAS_SCIPY')
@pytest.mark.parametrize('interval', ['root-n-0',
                                      'pearson',
                                      'sherpagehrels',
                                      'frequentist-confidence'])
def test_poisson_conf_large(interval):
    n = 100
    assert_allclose(funcs.poisson_conf_interval(n, interval='root-n'),
                    funcs.poisson_conf_interval(n, interval=interval),
                    rtol=2e-2)


def test_poisson_conf_array_rootn0_zero():
    n = np.zeros((3, 4, 5))
    assert_allclose(funcs.poisson_conf_interval(n, interval='root-n-0'),
                    funcs.poisson_conf_interval(n[0, 0, 0], interval='root-n-0')[:, None, None, None] * np.ones_like(n))

    assert not np.any(np.isnan(
        funcs.poisson_conf_interval(n, interval='root-n-0')))


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_array_frequentist_confidence_zero():
    n = np.zeros((3, 4, 5))
    assert_allclose(
        funcs.poisson_conf_interval(n, interval='frequentist-confidence'),
        funcs.poisson_conf_interval(n[0, 0, 0], interval='frequentist-confidence')[:, None, None, None] * np.ones_like(n))

    assert not np.any(np.isnan(
        funcs.poisson_conf_interval(n, interval='root-n-0')))


def test_poisson_conf_list_rootn0_zero():
    n = [0, 0, 0]
    assert_allclose(funcs.poisson_conf_interval(n, interval='root-n-0'),
                    [[0, 0, 0], [1, 1, 1]])

    assert not np.any(np.isnan(
        funcs.poisson_conf_interval(n, interval='root-n-0')))


def test_poisson_conf_array_rootn0():
    n = 7 * np.ones((3, 4, 5))
    assert_allclose(funcs.poisson_conf_interval(n, interval='root-n-0'),
                    funcs.poisson_conf_interval(n[0, 0, 0], interval='root-n-0')[:, None, None, None] * np.ones_like(n))

    n[1, 2, 3] = 0
    assert not np.any(np.isnan(
        funcs.poisson_conf_interval(n, interval='root-n-0')))


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_array_fc():
    n = 7 * np.ones((3, 4, 5))
    assert_allclose(
        funcs.poisson_conf_interval(n, interval='frequentist-confidence'),
        funcs.poisson_conf_interval(n[0, 0, 0], interval='frequentist-confidence')[:, None, None, None] * np.ones_like(n))

    n[1, 2, 3] = 0
    assert not np.any(np.isnan(
        funcs.poisson_conf_interval(n, interval='frequentist-confidence')))


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_frequentist_confidence_gehrels():
    """Test intervals against those published in Gehrels 1986"""
    nlh = np.array([(0, 0, 1.841),
                    (1, 0.173, 3.300),
                    (2, 0.708, 4.638),
                    (3, 1.367, 5.918),
                    (4, 2.086, 7.163),
                    (5, 2.840, 8.382),
                    (6, 3.620, 9.584),
                    (7, 4.419, 10.77),
                    (8, 5.232, 11.95),
                    (9, 6.057, 13.11),
                    (10, 6.891, 14.27),
                    ])
    assert_allclose(
        funcs.poisson_conf_interval(nlh[:, 0],
                                    interval='frequentist-confidence'),
        nlh[:, 1:].T, rtol=0.001, atol=0.001)


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_frequentist_confidence_gehrels_2sigma():
    """Test intervals against those published in Gehrels 1986

    Note: I think there's a typo (transposition of digits) in Gehrels 1986,
    specifically for the two-sigma lower limit for 3 events; they claim
    0.569 but this function returns 0.59623...

    """
    nlh = np.array([(0, 2, 0, 3.783),
                    (1, 2, 2.30e-2, 5.683),
                    (2, 2, 0.230, 7.348),
                    (3, 2, 0.596, 8.902),
                    (4, 2, 1.058, 10.39),
                    (5, 2, 1.583, 11.82),
                    (6, 2, 2.153, 13.22),
                    (7, 2, 2.758, 14.59),
                    (8, 2, 3.391, 15.94),
                    (9, 2, 4.046, 17.27),
                    (10, 2, 4.719, 18.58)])
    assert_allclose(
        funcs.poisson_conf_interval(nlh[:, 0], sigma=2,
                                    interval='frequentist-confidence').T,
        nlh[:, 2:], rtol=0.01)


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_frequentist_confidence_gehrels_3sigma():
    """Test intervals against those published in Gehrels 1986"""
    nlh = np.array([(0, 3, 0, 6.608),
                    (1, 3, 1.35e-3, 8.900),
                    (2, 3, 5.29e-2, 10.87),
                    (3, 3, 0.212, 12.68),
                    (4, 3, 0.465, 14.39),
                    (5, 3, 0.792, 16.03),
                    (6, 3, 1.175, 17.62),
                    (7, 3, 1.603, 19.17),
                    (8, 3, 2.068, 20.69),
                    (9, 3, 2.563, 22.18),
                    (10, 3, 3.084, 23.64),
                    ])
    assert_allclose(
        funcs.poisson_conf_interval(nlh[:, 0], sigma=3,
                                    interval='frequentist-confidence').T,
        nlh[:, 2:], rtol=0.01, verbose=True)


@pytest.mark.skipif('not HAS_SCIPY')
@pytest.mark.parametrize('n', [0, 1, 2, 3, 10, 20, 100])
def test_poisson_conf_gehrels86(n):
    assert_allclose(
        funcs.poisson_conf_interval(n, interval='sherpagehrels')[1],
        funcs.poisson_conf_interval(n, interval='frequentist-confidence')[1],
        rtol=0.02)


@pytest.mark.skipif('not HAS_SCIPY')
def test_scipy_poisson_limit():
    '''Test that the lower-level routine gives the snae number.

    Test numbers are from table1 1, 3 in
    Kraft, Burrows and Nousek in
    `ApJ 374, 344 (1991) <http://adsabs.harvard.edu/abs/1991ApJ...374..344K>`_
    '''
    assert_allclose(funcs._scipy_kraft_burrows_nousek(5., 2.5, .99),
                    (0, 10.67), rtol=1e-3)
    conf = funcs.poisson_conf_interval([5., 6.], 'kraft-burrows-nousek',
                                       background=[2.5, 2.],
                                       conflevel=[.99, .9])
    assert_allclose(conf[:, 0], (0, 10.67), rtol=1e-3)
    assert_allclose(conf[:, 1], (0.81, 8.99), rtol=5e-3)


@pytest.mark.skipif('not HAS_MPMATH')
def test_mpmath_poisson_limit():
    assert_allclose(funcs._mpmath_kraft_burrows_nousek(6., 2., .9),
                    (0.81, 8.99), rtol=5e-3)
    assert_allclose(funcs._mpmath_kraft_burrows_nousek(5., 2.5, .99),
                    (0, 10.67), rtol=1e-3)


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_value_errors():
    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval([5, 6], 'root-n', sigma=2)
    assert 'Only sigma=1 supported' in str(e.value)

    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval([5, 6], 'pearson', background=[2.5, 2.])
    assert 'background not supported' in str(e.value)

    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval([5, 6], 'sherpagehrels',
                                    conflevel=[2.5, 2.])
    assert 'conflevel not supported' in str(e.value)

    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval(1, 'foo')
    assert 'Invalid method' in str(e.value)


@pytest.mark.skipif('not HAS_SCIPY')
def test_poisson_conf_kbn_value_errors():
    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval(5., 'kraft-burrows-nousek',
                                    background=2.5,
                                    conflevel=99)
    assert 'number between 0 and 1' in str(e.value)

    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval(5., 'kraft-burrows-nousek',
                                    background=2.5)
    assert 'Set conflevel for method' in str(e.value)

    with pytest.raises(ValueError) as e:
        funcs.poisson_conf_interval(5., 'kraft-burrows-nousek',
                                    background=-2.5,
                                    conflevel=.99)
    assert 'Background must be' in str(e.value)


@pytest.mark.skipif('HAS_SCIPY or HAS_MPMATH')
def test_poisson_limit_nodependencies():
    with pytest.raises(ImportError):
        funcs.poisson_conf_interval(20., interval='kraft-burrows-nousek',
                                    background=10., conflevel=.95)
