from unittest import mock

import numpy as np
import pytest
from numpy import testing as npt
import scipy.signal as spsignal

from pyfar.dsp import filter
from pyfar.dsp.classes import FilterSOS
from pyfar.signal import Signal


def test_center_frequencies_iec():
    nominal_octs = [31.5, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    actual_octs = filter.center_frequencies_fractional_octaves(num_fractions=1)
    actual_octs_nom = actual_octs[0]
    npt.assert_allclose(actual_octs_nom, nominal_octs)

    nominal_thirds = [
        25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630,
        800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000,
        12500, 16000, 20000]
    actual_thirds = filter.center_frequencies_fractional_octaves(
        num_fractions=3)
    actual_thirds_nom = actual_thirds[0]
    npt.assert_allclose(actual_thirds_nom, nominal_thirds)

    with pytest.raises(ValueError, match="lower and upper limit"):
        filter.center_frequencies_fractional_octaves(frequency_range=(1,))

    with pytest.raises(ValueError, match="lower and upper limit"):
        filter.center_frequencies_fractional_octaves(frequency_range=(3, 4, 5))

    with pytest.raises(
            ValueError, match="second frequency needs to be higher"):
        filter.center_frequencies_fractional_octaves(
            frequency_range=(8e3, 1e3))

    with pytest.raises(ValueError, match="Number of fractions can only be"):
        filter.center_frequencies_fractional_octaves(5)

    actual_octs = filter.center_frequencies_fractional_octaves(
        num_fractions=1, frequency_range=(100, 4e3))
    actual_octs_nom = actual_octs[0]
    nominal_octs_part = [125, 250, 500, 1000, 2000, 4000]
    npt.assert_allclose(actual_octs_nom, nominal_octs_part)


def test_fractional_coeff_oct_filter_iec():
    sr = 48e3
    order = 2

    expected = np.array([
        [[1.99518917e-03,  3.99037834e-03,  1.99518917e-03,
          1.00000000e+00, -1.89455465e+00,  9.21866028e-01],
         [1.00000000e+00, -2.00000000e+00,  1.00000000e+00,
          1.00000000e+00, -1.94204953e+00,  9.52106382e-01]],
        [[7.47518158e-03,  1.49503632e-02,  7.47518158e-03,
          1.00000000e+00, -1.74644971e+00,  8.50561709e-01],
         [1.00000000e+00, -2.00000000e+00,  1.00000000e+00,
          1.00000000e+00, -1.86728468e+00,  9.06300424e-01]],
        [[2.65806645e-02,  5.31613291e-02,  2.65806645e-02,
          1.00000000e+00, -1.34871529e+00,  7.26916714e-01],
         [1.00000000e+00, -2.00000000e+00,  1.00000000e+00,
          1.00000000e+00, -1.67171842e+00,  8.18664740e-01]]])

    actual = filter._coefficients_fractional_octave_bands(
        sr, 1, freq_range=(1e3, 4e3), order=order)
    np.testing.assert_allclose(actual, expected)

    sr = 16e3
    order = 6

    actual = filter._coefficients_fractional_octave_bands(
        sr, 1, freq_range=(5e3, 20e3), order=order)

    assert actual.shape == (1, order, 6)


def test_fract_oct_filter_iec(impulse_mock):
    # Test only Filter object related stuff here, testing of coefficients is
    # done in separate test.
    sr = 48e3
    order = 2

    f_obj = filter.fractional_octave_bands(
        None, 3, sampling_rate=sr, order=order)
    assert isinstance(f_obj, FilterSOS)

    sig = filter.fractional_octave_bands(impulse_mock, 3, order=order)
    assert isinstance(sig, Signal)

    ir_actual = filter.fractional_octave_bands(
        impulse_mock, 1, freq_range=(1e3, 4e3), order=order)

    assert ir_actual.time.shape[0] == 3


def test_extend_sos_coefficients():
    sos = np.array([
        [1, 0, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 0],
    ])

    expected = np.array([
        [1, 0, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 0],
        [1, 0, 0, 1, 0, 0],
    ])

    actual = filter._extend_sos_coefficients(sos, 4)
    npt.assert_allclose(actual, expected)

    # test if the extended filter has an ideal impulse response.
    imp = np.zeros(512)
    imp[0] = 1
    imp_filt = spsignal.sosfilt(actual, imp)
    npt.assert_allclose(imp_filt, imp)


@pytest.fixture
def impulse_mock():
    """ Generate impulse signals, in order to test independently of the Signal
    object.

    Returns
    -------
    signal : Signal
        single channel dirac signal, delay 0 samples, length 1024 samples,
        sampling rate 44.1 kHz

    """
    n_samples = 1024
    n_bins = int(n_samples / 2 + 1)
    sampling_rate = 48e3
    times = np.arange(0, n_samples) / sampling_rate
    frequencies = np.arange(n_bins) * sampling_rate / n_bins

    # time signal:
    time = np.zeros(n_samples, dtype='float64')
    time[0] = 1

    # frequency signal
    freq = np.ones(n_bins)

    # create a mock object of Signal class to test the plot independently
    signal = mock.Mock(spec_set=Signal(time, sampling_rate))
    signal.sampling_rate = sampling_rate
    signal.time = time[np.newaxis, :]
    signal.times = times
    signal.n_samples = n_samples
    signal.freq = freq[np.newaxis, :]
    signal.frequencies = frequencies
    signal.n_bins = n_bins
    signal.cshape = (1, )
    signal.signal_type = 'energy'
    signal.fft_norm = 'unitary'

    return signal
