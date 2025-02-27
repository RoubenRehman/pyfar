import numpy as np
import numpy.testing as npt

import pytest
from pyfar.dsp import fft


def test_n_bins_even():
    n_samples = 6
    truth = int(n_samples/2 + 1)
    n_bins = fft._n_bins_from_n_samples(n_samples)
    assert n_bins == truth


def test_n_bins_odd():
    n_samples = 7
    truth = int((n_samples + 1)/2)
    n_bins = fft._n_bins_from_n_samples(n_samples)
    assert n_bins == truth


def test_n_bins_complex():
    n_samples = 6
    truth = n_samples
    n_bins = fft._n_bins_from_n_samples(n_samples, complex_time=True)
    assert n_bins == truth


def test_n_samples():
    n_bins = 6
    truth = int(n_bins-1) * 2
    n_samples = fft._n_samples_from_n_bins(n_bins)
    assert n_samples == truth


def test_n_samples_complex():
    n_bins = 7
    truth = n_bins
    n_samples = fft._n_samples_from_n_bins(n_bins, is_complex=True)
    assert n_samples == truth


def test_fft_orthogonality_sine_even(sine_stub):
    signal_spec = fft.rfft(
        sine_stub.time, sine_stub.n_samples, sine_stub.sampling_rate,
        sine_stub.fft_norm)
    transformed_signal_time = fft.irfft(
        signal_spec, sine_stub.n_samples, sine_stub.sampling_rate,
        sine_stub.fft_norm)
    npt.assert_allclose(
        transformed_signal_time, sine_stub.time,
        rtol=1e-10, atol=10*np.finfo(float).eps)


def test_fft_orthogonality_sine_odd(sine_stub_odd):
    signal_spec = fft.rfft(
        sine_stub_odd.time, sine_stub_odd.n_samples,
        sine_stub_odd.sampling_rate, sine_stub_odd.fft_norm)
    transformed_signal_time = fft.irfft(
        signal_spec, sine_stub_odd.n_samples, sine_stub_odd.sampling_rate,
        sine_stub_odd.fft_norm)
    npt.assert_allclose(
        transformed_signal_time, sine_stub_odd.time,
        rtol=1e-10, atol=10*np.finfo(float).eps)


def test_fft_orthogonality_noise_even(noise_stub):
    signal_spec = fft.rfft(
        noise_stub.time, noise_stub.n_samples, noise_stub.sampling_rate,
        noise_stub.fft_norm)
    transformed_signal_time = fft.irfft(
        signal_spec, noise_stub.n_samples, noise_stub.sampling_rate,
        noise_stub.fft_norm)
    npt.assert_allclose(
        transformed_signal_time, noise_stub.time,
        rtol=1e-10, atol=10*np.finfo(float).eps)


def test_fft_orthogonality_noise_odd(noise_stub_odd):
    signal_spec = fft.rfft(
        noise_stub_odd.time, noise_stub_odd.n_samples,
        noise_stub_odd.sampling_rate, noise_stub_odd.fft_norm)
    transformed_signal_time = fft.irfft(
        signal_spec, noise_stub_odd.n_samples, noise_stub_odd.sampling_rate,
        noise_stub_odd.fft_norm)
    npt.assert_allclose(
        transformed_signal_time, noise_stub_odd.time,
        rtol=1e-10, atol=10*np.finfo(float).eps)


def test_fft_parseval_theorem_sine_even(sine_stub):
    signal_spec = fft.rfft(
        sine_stub.time, sine_stub.n_samples,
        sine_stub.sampling_rate, sine_stub.fft_norm)

    e_time = np.mean(np.abs(sine_stub.time)**2)
    e_freq = np.sum(np.abs(signal_spec)**2)

    npt.assert_allclose(e_freq, e_time, rtol=1e-10)


def test_fft_parseval_theorem_sine_odd(sine_stub_odd):
    signal_spec = fft.rfft(
        sine_stub_odd.time, sine_stub_odd.n_samples,
        sine_stub_odd.sampling_rate, sine_stub_odd.fft_norm)

    e_time = np.mean(np.abs(sine_stub_odd.time)**2)
    e_freq = np.sum(np.abs(signal_spec)**2)

    npt.assert_allclose(e_freq, e_time, rtol=1e-10)


def test_fft_parseval_theorem_noise_even(noise_stub):
    signal_spec = fft.rfft(
        noise_stub.time, noise_stub.n_samples, noise_stub.sampling_rate,
        noise_stub.fft_norm)

    e_time = np.mean(np.abs(noise_stub.time)**2)
    e_freq = np.sum(np.abs(signal_spec)**2)

    npt.assert_allclose(e_freq, e_time, rtol=1e-10)


def test_fft_parseval_theorem_noise_odd(noise_stub_odd):
    signal_spec = fft.rfft(
        noise_stub_odd.time, noise_stub_odd.n_samples,
        noise_stub_odd.sampling_rate, noise_stub_odd.fft_norm)

    e_time = np.mean(np.abs(noise_stub_odd.time)**2)
    e_freq = np.sum(np.abs(signal_spec)**2)

    npt.assert_allclose(e_freq, e_time, rtol=1e-10)


def test_is_odd():
    num = 3
    assert fft._is_odd(num)


def test_is_not_odd():
    num = 4
    assert not fft._is_odd(num)


def test_normalization_none(impulse_stub):
    spec_out = fft.normalization(
        impulse_stub.freq.copy(), impulse_stub.n_samples,
        impulse_stub.sampling_rate, impulse_stub.fft_norm, inverse=False)
    npt.assert_allclose(
        spec_out, impulse_stub.freq, atol=10*np.finfo(float).eps)

    spec_out = fft.normalization(
        impulse_stub.freq.copy(), impulse_stub.n_samples,
        impulse_stub.sampling_rate, impulse_stub.fft_norm, inverse=True)
    npt.assert_allclose(
        spec_out, impulse_stub.freq, atol=10*np.finfo(float).eps)


def test_normalization_single_sided_single_channel_even_samples():
    # single sided test spectrum
    v = 1/3 + 1/3j
    vsq = np.abs(v)**2
    spec_single = np.array([v, v, v])
    # valid number of samples of time signal corresponding to spec_single
    N = 4       # time signal with even number of samples
    Nsq = N**2  # factor for power and psd normalization
    fs = 40     # arbitrary sampling frequency for psd normalization

    # expected results for even number of samples
    sqrt2 = np.sqrt(2)
    truth = {
        'unitary': np.array([v, v * 2, v]),
        'amplitude': np.array([v / N,
                               v / N * 2,
                               v / N]),
        'rms': np.array([v / N,
                         v / N / sqrt2 * 2,
                         v / N]),
        'power': np.array([vsq / Nsq,
                           vsq / Nsq * 2,
                           vsq / Nsq]),
        'psd': np.array([vsq / N / fs,
                         vsq / N / fs * 2,
                         vsq / N / fs]),
    }

    for normalization in truth:
        print(f"Assesing normalization: '{normalization}'")
        spec_out = fft.normalization(spec_single.copy(), N, fs,
                                     normalization, inverse=False)
        npt.assert_allclose(spec_out, truth[normalization], atol=1e-15)

        print(f"Assesing normalization: '{normalization}' (inverse)")
        spec_out_inv = fft.normalization(spec_out, N, fs,
                                         normalization, inverse=True)
        if normalization in ['power', 'psd']:
            # Inverse only resembles magnitude for power norms
            npt.assert_allclose(spec_out_inv, np.abs(spec_single), atol=1e-15)
        else:
            npt.assert_allclose(spec_out_inv, spec_single, atol=1e-15)


def test_normalization_single_sided_single_channel_odd_samples():
    # single sided test spectrum
    v = 1/3 + 1/3j
    vsq = np.abs(v)**2
    spec_single = np.array([v, v, v])
    # valid number of samples of time signal corresponding to spec_single
    N = 5       # time signal with even number of samples
    Nsq = N**2  # factor for power and psd normalization
    fs = 50     # arbitrary sampling frequency for psd normalization

    # expected results for even number of samples
    sqrt2 = np.sqrt(2)
    truth = {
        'unitary': np.array([v, v * 2, v * 2]),
        'amplitude': np.array([v / N,
                               v / N * 2,
                               v / N * 2]),
        'rms': np.array([v / N,
                         v / N / sqrt2 * 2,
                         v / N / sqrt2 * 2]),
        'power': np.array([vsq / Nsq,
                           vsq / Nsq * 2,
                           vsq / Nsq * 2]),
        'psd': np.array([vsq / N / fs,
                         vsq / N / fs * 2,
                         vsq / N / fs * 2]),
    }

    for normalization in truth:
        print(f"Assesing normalization: '{normalization}'")
        spec_out = fft.normalization(spec_single.copy(), N, fs,
                                     normalization, inverse=False)
        npt.assert_allclose(spec_out, truth[normalization], atol=1e-15)

        print(f"Assesing normalization: '{normalization}' (inverse)")
        spec_out_inv = fft.normalization(spec_out, N, fs,
                                         normalization, inverse=True)
        if normalization in ['power', 'psd']:
            # Inverse only resembles magnitude for power norms
            npt.assert_allclose(spec_out_inv, np.abs(spec_single), atol=1e-15)
        else:
            npt.assert_allclose(spec_out_inv, spec_single, atol=1e-15)


def test_normalization_both_sided_single_channel():
    # single sided test spectrum
    v = 1/3 + 1/3j
    vsq = np.abs(v)**2
    spec_single = np.array([v, v, v])
    # valid number of samples of time signal corresponding to spec_single
    N = 3       # time signal with even number of samples
    Nsq = N**2  # factor for power and psd normalization
    fs = 30     # arbitrary sampling frequency for psd normalization

    # expected results for even number of samples
    truth = {
        'unitary': np.array([v, v, v]),
        'amplitude': np.array([v / N,
                               v / N,
                               v / N]),
        'power': np.array([vsq / Nsq,
                           vsq / Nsq,
                           vsq / Nsq]),
        'psd': np.array([vsq / N / fs,
                         vsq / N / fs,
                         vsq / N / fs]),
    }

    for normalization in truth:
        print(f"Assesing normalization: '{normalization}'")
        spec_out = fft.normalization(spec_single.copy(), N, fs,
                                     normalization, inverse=False,
                                     single_sided=False)
        npt.assert_allclose(spec_out, truth[normalization], atol=1e-15)

        print(f"Assesing normalization: '{normalization}' (inverse)")
        spec_out_inv = fft.normalization(spec_out, N, fs,
                                         normalization, inverse=True,
                                         single_sided=False)
        if normalization in ['power', 'psd']:
            # Inverse only resembles magnitude for power norms
            npt.assert_allclose(spec_out_inv, np.abs(spec_single), atol=1e-15)
        else:
            npt.assert_allclose(spec_out_inv, spec_single, atol=1e-15)


def test_normalization_single_sided_multi_channel_even_samples():
    # single sided test spectrum
    v = 1/3 + 1/3j
    vsq = np.abs(v)**2
    tile = (4, 2, 1)
    spec_single = np.tile(np.array([v, v, v]), tile)
    # valid number of samples of time signal corresponding to spec_single
    N = 4       # time signal with even number of samples
    Nsq = N**2  # factor for power and psd normalization
    fs = 40     # arbitrary sampling frequency for psd normalization

    # expected results for even number of samples
    sqrt2 = np.sqrt(2)
    truth = {
        'unitary': np.array([v, v * 2, v]),
        'amplitude': np.array([v / N,
                               v / N * 2,
                               v / N]),
        'rms': np.array([v / N,
                         v / N / sqrt2 * 2,
                         v / N]),
        'power': np.array([vsq / Nsq,
                           vsq / Nsq * 2,
                           vsq / Nsq]),
        'psd': np.array([vsq / N / fs,
                         vsq / N / fs * 2,
                         vsq / N / fs]),
    }

    for normalization in truth:
        print(f"Assesing normalization: '{normalization}'")
        spec_out = fft.normalization(spec_single.copy(), N, fs,
                                     normalization, inverse=False)
        npt.assert_allclose(spec_out, np.tile(truth[normalization], tile),
                            atol=1e-15)

        print(f"Assesing normalization: '{normalization}' (inverse)")
        spec_out_inv = fft.normalization(spec_out, N, fs,
                                         normalization, inverse=True)
        if normalization in ['power', 'psd']:
            # Inverse only resembles magnitude for power norms
            npt.assert_allclose(spec_out_inv, np.abs(spec_single), atol=1e-15)
        else:
            npt.assert_allclose(spec_out_inv, spec_single, atol=1e-15)


def test_normalization_with_window():
    """
    Test if the window cancels out if applying the normalization and
    inverse normalization.
    """

    # test with window as list and numpy array
    windows = [[1, 1, 1, 1], np.array([1, 1, 1, 1])]

    fft_norms = ['unitary', 'amplitude', 'rms', 'power', 'psd']
    for window in windows:
        for fft_norm in fft_norms:
            print(f"testing: {window}, {fft_norm}")
            spec = fft.normalization(np.array([.5, 1, .5]), 4, 44100,
                                     fft_norm, window=window)
            spec = fft.normalization(spec, 4, 44100, fft_norm,
                                     inverse=True, window=window)
            npt.assert_allclose(spec, np.array([.5, 1, .5]), atol=1e-15)


def test_normalization_with_window_value_error():
    """
    Test if normalization throws a ValueError if the window has the
    wrong length.
    """

    match = 'window must be 4 long but is 5 long.'
    with pytest.raises(ValueError, match=match):
        # n_samples=5, and len(window)=5
        fft.normalization(np.array([.5, 1, .5]), 4, 44100,
                          'amplitude', window=[1, 1, 1, 1, 1])


def test_normalization_exceptions():
    # Call without numpy array
    match = "Input 'spec' must be a numpy array."
    with pytest.raises(ValueError, match=match):
        fft.normalization(1, 1, 44100, 'rms')
    # Invalid normalization
    match = "norm type must be 'unitary', 'amplitude', 'rms', "\
        "'power', or 'psd' but is 'goofy'"

    with pytest.raises(ValueError, match=match):
        fft.normalization(np.array([1]), 1, 44100, 'goofy')


def test_rfft_normalization_impulse(impulse_stub):
    """Test for call of normalization in rfft.
    """
    signal_spec = fft.rfft(
        impulse_stub.time, impulse_stub.n_samples, impulse_stub.sampling_rate,
        impulse_stub.fft_norm)

    npt.assert_allclose(
        signal_spec, impulse_stub.freq,
        rtol=1e-10, atol=1e-10)


def test_rfft_normalization_sine(sine_stub):
    """Test for correct call of normalization in rfft.
    """
    signal_spec = fft.rfft(
        sine_stub.time, sine_stub.n_samples, sine_stub.sampling_rate,
        sine_stub.fft_norm)

    npt.assert_allclose(
        signal_spec, sine_stub.freq,
        rtol=1e-10, atol=1e-10)


def test_fft_add_mirror_spec():
    """Test method to add mirror spectrum to single-sided frequency data."""
    data_odd = [1, 2, 3, 4, 5, 6, 7]
    fr_odd = fft.rfft(data_odd, n_samples=7, sampling_rate=48000,
                      fft_norm='none')
    fr_odd_both = fft.add_mirror_spectrum(fr_odd, even_samples=False)
    fr_odd_desired = fft.fft(data_odd, n_samples=7, sampling_rate=48000,
                             fft_norm='none')

    npt.assert_allclose(
        fr_odd_both, fr_odd_desired,
        rtol=1e-12)

    data_even = [1, 2, 3, 4, 5, 6]
    fr_even = fft.rfft(data_even, n_samples=6, sampling_rate=48000,
                       fft_norm='none')
    fr_even_both = fft.add_mirror_spectrum(fr_even, even_samples=True)
    fr_even_desired = fft.fft(data_even, n_samples=6, sampling_rate=48000,
                              fft_norm='none')
    npt.assert_allclose(
        fr_even_both, fr_even_desired,
        rtol=1e-12)


def test_fft_remove_mirror_spec():
    """Test method to remove redundant part of double-sided frequency data."""
    data_odd = [1, 2, 3, 4, 5, 6, 7]
    fr_odd_desired = fft.rfft(data_odd, n_samples=7, sampling_rate=48000,
                              fft_norm='none')
    fr_odd = fft.fft(data_odd, n_samples=7, sampling_rate=48000,
                     fft_norm='none')
    fr_odd_single = fft.remove_mirror_spectrum(fr_odd)

    npt.assert_allclose(
        fr_odd_single, fr_odd_desired,
        rtol=1e-12)

    data_even = [1, 2, 3, 4, 5, 6]
    fr_even_desired = fft.rfft(data_even, n_samples=6, sampling_rate=48000,
                               fft_norm='none')
    fr_even = fft.fft(data_even, n_samples=6, sampling_rate=48000,
                      fft_norm='none')
    fr_even_single = fft.remove_mirror_spectrum(fr_even)

    npt.assert_allclose(
        fr_even_single, fr_even_desired,
        rtol=1e-12)


def test_check_conjugate_symmetry():
    """Test checking for conjugate symmetry."""

    sampling_rate = 48000
    fft_norm = 'none'

    # test _check_conjugate_symmetry with conjugate
    # symmetric frequency data with even number of samples
    n_samples = 4
    data = np.array([1, 2, 3, 4])
    assert fft._check_conjugate_symmetry(
        fft.fft(data, n_samples, sampling_rate, fft_norm))

    # test _check_conjugate_symmetry with conjugate
    # symmetric frequency data with odd number of samples
    n_samples = 5
    data = np.array([1, 2, 3, 4, 5])
    assert fft._check_conjugate_symmetry(
        fft.fft(data, n_samples, sampling_rate, fft_norm))

    # test _check_conjugate_symmetry with non conjugate
    # symmetric frequency data with even number of samples
    n_samples = 4
    data = np.array([1+1j, 2+2j, 3+3j, 4+4j])
    assert not fft._check_conjugate_symmetry(
        fft.fft(data, n_samples, sampling_rate, fft_norm))

    # test _check_conjugate_symmetry with non conjugate
    # symmetric frequency data with odd number of samples
    n_samples = 5
    data = np.array([1+1j, 2+2j, 3+3j, 4+4j, 5+5j])
    assert not fft._check_conjugate_symmetry(
        fft.fft(data, n_samples, sampling_rate, fft_norm))
