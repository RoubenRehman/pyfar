import pytest
import numpy as np
import numpy.testing as npt
import os
import pyfar as pf
from pyfar import Signal
import pyfar.dsp.filter as pfilt
import pyfar.classes.filter as pclass


def test_butterworth(impulse):
    # Uses scipy function. We thus only test the functionality not the results
    # Filter object
    f_obj = pfilt.butterworth(None, 2, 1000, 'lowpass', 44100)
    assert isinstance(f_obj, pclass.FilterSOS)
    assert f_obj.comment == ("Butterworth lowpass of order 2. "
                             "Cut-off frequency 1000 Hz.")

    # Filter
    x = pfilt.butterworth(impulse, 2, 1000, 'lowpass')
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.butterworth(impulse, 2, 1000, 'lowpass', 44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.butterworth(None, 2, 1000, 'lowpass')


def test_chebyshev1(impulse):
    # Uses scipy function. We thus only test the functionality not the results
    # Filter object
    f_obj = pfilt.chebyshev1(None, 2, 1, 1000, 'lowpass', 44100)
    assert isinstance(f_obj, pclass.FilterSOS)
    assert f_obj.comment == ("Chebychev Type I lowpass of order 2. "
                             "Cut-off frequency 1000 Hz. "
                             "Pass band ripple 1 dB.")

    # Filter
    x = pfilt.chebyshev1(impulse, 2, 1, 1000, 'lowpass')
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.chebyshev1(impulse, 2, 1, 1000, 'lowpass', 44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.chebyshev1(None, 2, 1, 1000, 'lowpass')


def test_chebyshev2(impulse):
    # Uses scipy function. We thus only test the functionality not the results
    # Filter object
    f_obj = pfilt.chebyshev2(None, 2, 40, 1000, 'lowpass', 44100)
    assert isinstance(f_obj, pclass.FilterSOS)
    assert f_obj.comment == ("Chebychev Type II lowpass of order 2. "
                             "Cut-off frequency 1000 Hz. "
                             "Stop band attenuation 40 dB.")

    # Filter
    x = pfilt.chebyshev2(impulse, 2, 40, 1000, 'lowpass')
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.chebyshev2(impulse, 2, 40, 1000, 'lowpass', 44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.chebyshev2(None, 2, 40, 1000, 'lowpass')


def test_elliptic(impulse):
    # Uses scipy function. We thus only test the functionality not the results
    # Filter object
    f_obj = pfilt.elliptic(None, 2, 1, 40, 1000, 'lowpass', 44100)
    assert isinstance(f_obj, pclass.FilterSOS)
    assert f_obj.comment == ("Elliptic (Cauer) lowpass of order 2. "
                             "Cut-off frequency 1000 Hz. "
                             "Pass band ripple 1 dB. "
                             "Stop band attenuation 40 dB.")

    # Filter
    x = pfilt.elliptic(impulse, 2, 1, 40, 1000, 'lowpass')
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.elliptic(impulse, 2, 1, 40, 1000, 'lowpass', 44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.elliptic(None, 2, 1, 40, 1000, 'lowpass')


def test_bessel(impulse):
    # Uses scipy function. We thus only test the functionality not the results
    # Filter object
    f_obj = pfilt.bessel(None, 2, 1000, 'lowpass', 'phase', 44100)
    assert isinstance(f_obj, pclass.FilterSOS)
    assert f_obj.comment == ("Bessel/Thomson lowpass of order 2 and 'phase' "
                             "normalization. Cut-off frequency 1000 Hz.")

    # Filter
    x = pfilt.bessel(impulse, 2, 1000, 'lowpass', 'phase')
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.bessel(impulse, 2, 1000, 'lowpass', 'phase', 44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.bessel(None, 2, 1000, 'lowpass', 'phase')


@pytest.mark.parametrize('order', [1, 2])
def test_allpass(impulse, order):
    # Uses third party code.
    # We thus only test the functionality not the results
    fc = 1033

    sig_filt = pfilt.allpass(impulse, fc, order)
    gd = pf.dsp.group_delay(sig_filt)

    # Group delay at w = 0
    T_gr_0 = gd[0, 0]
    # definition of group delay at fc (Tietze et al.)
    T_fc_desired = T_gr_0 * (1 / np.sqrt(2))
    # id of frequency bin closest to fc
    idx = sig_filt.find_nearest_frequency(fc)
    # group delay below fc and at fc
    T_below = gd[0, :idx]
    T_fc = gd[0, idx]

    # tolerance for group delay below fc
    tol = 1 - (T_fc / T_gr_0)

    # Test if group delay at fc is correct
    np.testing.assert_allclose(T_fc_desired, T_fc, rtol=0.01)
    # Test group delay below fc
    np.testing.assert_allclose(T_below, T_gr_0, rtol=tol)

    f_obj = pfilt.allpass(None, fc, order, sampling_rate=44100)
    assert isinstance(f_obj, pclass.FilterIIR)
    assert f_obj.comment == (
        f"Allpass of order {order} with cutoff frequency "
        f"{fc} Hz.")

    # Filter
    x = pfilt.allpass(impulse, fc, order)
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)


def test_allpass_warnings(impulse, fc=1000):
    # test ValueError
    with pytest.raises(ValueError,
                       match='Either signal or sampling_rate must be none.'):
        # pass signal and sampling rate
        pfilt.allpass(impulse, fc, 1, sampling_rate=44100)
    with pytest.raises(ValueError,
                       match='Either signal or sampling_rate must be none.'):
        # pass no signal and no sampling rate
        pfilt.allpass(None, fc, 1)
    with pytest.raises(ValueError,
                       match='Order must be 1 or 2'):
        # pass wrong order
        pfilt.allpass(impulse, fc, 3)
    with pytest.raises(ValueError,
                       match='Coefficients must match the allpass order'):
        # pass wrong combination of coefficients and order
        pfilt.allpass(impulse, fc, 1, [1, 2])
    with pytest.raises(ValueError,
                       match='Coefficients must match the allpass order'):
        # pass wrong combination of coefficients and order
        pfilt.allpass(impulse, fc, 2, 1)


def test_bell(impulse):
    # Uses third party code.
    # We thus only test the functionality not the results
    # Filter object
    f_obj = pfilt.bell(None, 1000, 10, 2, sampling_rate=44100)
    assert isinstance(f_obj, pclass.FilterIIR)
    assert f_obj.comment == (
        "Second order bell (parametric equalizer) of "
        "type II with 10 dB gain at 1000 Hz (Quality = 2).")

    # Filter
    x = pfilt.bell(impulse, 1000, 10, 2)
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # test ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.bell(impulse, 1000, 10, 2, sampling_rate=44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.bell(None, 1000, 10, 2)
    # check wrong input arguments
    match = "bell_type must be 'I', 'II' or 'III' but is 'nope'.'"
    with pytest.raises(ValueError, match=match):
        x = pfilt.bell(impulse, 1000, 10, 2, bell_type='nope')
    match = "quality_warp must be 'cos', 'sin' or 'tan' but is 'nope'.'"
    with pytest.raises(ValueError, match=match):
        x = pfilt.bell(impulse, 1000, 10, 2, quality_warp='nope')


def test_shelf(impulse):
    # Uses third party code.
    # We thus only test the functionality not the results

    shelves = [pfilt.low_shelf, pfilt.high_shelf]
    kinds = ['Low', 'High']

    for shelf, kind in zip(shelves, kinds):
        # Filter object
        f_obj = shelf(None, 1000, 10, 2, sampling_rate=44100)
        assert isinstance(f_obj, pclass.FilterIIR)
        assert f_obj.comment == (f"{kind}-shelf of order 2 and type I with "
                                 "10 dB gain at 1000 Hz.")

        # Filter
        x = shelf(impulse, 1000, 10, 2)
        y = f_obj.process(impulse)
        assert isinstance(x, Signal)
        npt.assert_allclose(x.time, y.time)

        # ValueError
        match = 'Either signal or sampling_rate must be none.'
        with pytest.raises(ValueError, match=match):
            # pass signal and sampling rate
            x = shelf(impulse, 1000, 10, 2, sampling_rate=44100)
        match = 'Either signal or sampling_rate must be none.'
        with pytest.raises(ValueError, match=match):
            # pass no signal and no sampling rate
            x = shelf(None, 1000, 10, 2)
        # check wrong input arguments
        match = "shelf_type must be 'I', 'II' or 'III' but is 'nope'.'"
        with pytest.raises(ValueError, match=match):
            x = shelf(impulse, 1000, 10, 2, shelf_type='nope')
        match = 'order must be 1 or 2 but is 3'
        with pytest.raises(ValueError, match=match):
            x = shelf(impulse, 1000, 10, 3)


def test_crossover(impulse):
    # Uses scipy function. We thus mostly test the functionality not the
    # results

    # Filter object
    f_obj = pfilt.crossover(None, 2, 1000, 44100)
    assert isinstance(f_obj, pclass.FilterSOS)
    assert f_obj.comment == ("Linkwitz-Riley cross over network of order 2 at "
                             "1000 Hz.")

    # test filter
    x = pfilt.crossover(impulse, 2, 1000)
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # test ValueError
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.crossover(impulse, 2, 1000, 44100)
    match = 'Either signal or sampling_rate must be none.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.crossover(None, 2, 1000)
    match = "The order 'N' must be an even number."
    with pytest.raises(ValueError, match=match):
        # odd filter order
        x = pfilt.crossover(impulse, 3, 1000)

    # check if frequency response sums to unity for different filter orders
    # and cross-over frequencies
    for order in [2, 4, 6, 8]:
        for frequency in [4000, (1e2, 10e3)]:
            x = pfilt.crossover(impulse, order, frequency)
            x_sum = np.sum(x.freq, axis=-3).flatten()
            x_ref = np.ones(x.n_bins)
            npt.assert_allclose(x_ref, np.abs(x_sum), atol=.0005)

    # check network with multiple cross-over frequencies
    f_obj = pfilt.crossover(None, 2, [100, 10_000], 44100)
    assert f_obj.comment == ("Linkwitz-Riley cross over network of order 2 at "
                             "100, 10000 Hz.")


def test_reconstructing_fractional_octave_bands():
    """Test the reconstructing fractional octave filter bank."""

    # test filter object
    f_obj, f = pfilt.reconstructing_fractional_octave_bands(
        None, sampling_rate=44100)
    assert isinstance(f_obj, pclass.FilterFIR)
    assert f_obj.comment == \
        ("Reconstructing linear phase fractional octave filter bank."
         "(num_fractions=1, frequency_range=(63, 16000), overlap=1, slope=0)")
    assert f_obj.sampling_rate == 44100

    # test frequencies
    _, f_test = pfilt.fractional_octave_frequencies(
        frequency_range=(63, 16000))
    npt.assert_allclose(f, f_test)

    # test filtering
    x = pf.signals.impulse(2**12)
    y, f = pfilt.reconstructing_fractional_octave_bands(x)
    assert isinstance(y, Signal)
    assert y.cshape == (9, 1)
    assert y.fft_norm == 'none'

    # test reconstruction (sum has a group delay of half the filter length)
    reference = pf.signals.impulse(2**12, 2**11)
    y_sum = y.copy()
    y_sum.time = np.sum(y_sum.time, 0)
    npt.assert_allclose(y_sum.time, reference.time, atol=1e-6)


def test_reconstructing_fractional_octave_bands_filter_slopes():
    """Test the shape of the filter slopes for different parameters."""
    # test different filter slopes against reference
    x = pf.signals.impulse(2**10)

    for overlap, slope in zip([1, 1, 0], [0, 3, 0]):
        y, _ = pfilt.reconstructing_fractional_octave_bands(
            x, frequency_range=(8e3, 16e3), overlap=overlap, slope=slope,
            n_samples=2**10)
        reference = np.loadtxt(os.path.join(
            os.path.dirname(__file__), "references",
            f"filter.reconstructing_octaves_{overlap}_{slope}.csv"))
        # restricting rtol was not needed locally. It was added for tests to
        # pass on the testing platform
        npt.assert_allclose(
            y.time[:, 0, :], np.atleast_2d(reference), rtol=.01, atol=1e-10)


def test_reconstructing_fractional_octave_bands_warning():
    """Test warning for octave frequency exceeding half the sampling rate."""
    with pytest.warns(UserWarning):
        x = pf.signals.impulse(2**12, sampling_rate=16e3)
        y, f = pfilt.reconstructing_fractional_octave_bands(x)


def test_notch(impulse):
    """Test notch filter behavior."""
    f_obj = pfilt.notch(None, 1e3, 1, 44100)
    assert isinstance(f_obj, pclass.FilterIIR)
    assert f_obj.comment == ("Second order notch filter at "
                             "1000.0 Hz (Quality = 1).")

    # Filter
    x = pfilt.notch(impulse, 1e3, 1)
    y = f_obj.process(impulse)
    assert isinstance(x, Signal)
    npt.assert_allclose(x.time, y.time)

    # ValueError
    match = 'Either signal or sampling_rate must be None.'
    with pytest.raises(ValueError, match=match):
        # pass signal and sampling rate
        x = pfilt.notch(impulse, 1e3, 1, 44100)
    match = 'Either signal or sampling_rate must be None.'
    with pytest.raises(ValueError, match=match):
        # pass no signal and no sampling rate
        x = pfilt.notch(None, 1e3, 1)


@pytest.mark.parametrize("f", [1e3, 4e3])
@pytest.mark.parametrize("Q", [1, 10])
def test_notch_result(f, Q):
    """Test the frequency response of the notch filter."""
    # generate and apply notch filter
    notch = pf.dsp.filter.notch(pf.signals.impulse(44100), f, Q)

    # test characteristic points of frequency response
    npt.assert_almost_equal(np.abs(notch.freq_raw[0, int(f)]), 0, 12)
    npt.assert_almost_equal(np.abs(notch.freq_raw[0, 0]), 1, 12)
    npt.assert_almost_equal(np.abs(notch.freq_raw[0, -1]), 1, 12)

    # estimate and test actual quality
    mask = pf.dsp.decibel(notch) <= -3
    mask = mask.flatten()
    bandwidth = np.max(notch.frequencies[mask]) - \
        np.min(notch.frequencies[mask])
    bandwidth /= f
    Q_act = 1 / bandwidth
    # precision could be increased by increasing the impulse length
    npt.assert_allclose(Q_act, Q, rtol=.01, atol=.2)
