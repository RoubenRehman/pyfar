import os
import pytest
from pytest import raises
import matplotlib.pyplot as plt
import pyfar as pf
import pyfar.plot as plot
from pyfar.testing.plot_utils import create_figure, save_and_compare
import numpy as np
import numpy.testing as npt

# global parameters -----------------------------------------------------------
# flag for creating new baseline plots
# - required if the plot look changed
# - make sure to manually check the new baseline plots located at baseline_path
create_baseline = False

# file type used for saving the plots
file_type = "png"

# if true, the plots will be compared to the baseline and an error is raised
# if there are any differences. In any case, differences are written to
# output_path as images
compare_output = False

# path handling
base_path = os.path.join('tests', 'test_plot_data')
baseline_path = os.path.join(base_path, 'baseline')
output_path = os.path.join(base_path, 'output')

if not os.path.isdir(base_path):
    os.mkdir(base_path)
if not os.path.isdir(baseline_path):
    os.mkdir(baseline_path)
if not os.path.isdir(output_path):
    os.mkdir(output_path)

# remove old output files
for file in os.listdir(output_path):
    os.remove(os.path.join(output_path, file))


# testing ---------------------------------------------------------------------
@pytest.mark.parametrize('function', [
    (plot.time), (plot.freq), (plot.phase), (plot.group_delay),
    (plot.time_freq), (plot.freq_phase), (plot.freq_group_delay)])
def test_line_plots(function, handsome_signal, handsome_signal_v2):
    """Test all line plots with default arguments and hold functionality."""
    print(f"Testing: {function.__name__}")

    # initial plot
    filename = function.__name__ + '_default'
    create_figure()
    function(handsome_signal)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)

    # test hold functionality
    filename = function.__name__ + '_hold'
    function(handsome_signal_v2)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('param', [
    ['phase_deg', True, False],
    ['phase_unwrap', False, True],
    ['phase_deg_unwrap', True, True]])
def test_line_phase_options(param, handsome_signal):
    """Test parameters that are unique to the phase plot."""
    print(f"Testing: {param[0]}")

    filename = param[0]
    create_figure()
    plot.phase(handsome_signal, deg=param[1], unwrap=param[2])
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


def test_line_phase_unwrap_assertion(sine):
    """Test assertion for unwrap parameter."""
    with raises(ValueError):
        plot.phase(sine, unwrap='infinity')


@pytest.mark.parametrize('function', [
    (plot.time), (plot.freq), (plot.spectrogram)])
def test_line_dB_option(function, handsome_signal):
    """Test all line plots that have a dB option."""
    # test if dB option is working
    for dB in [True, False]:
        print(f"Testing: {function.__name__} (dB={dB})")

        filename = function.__name__ + '_dB_' + str(dB)
        create_figure()
        function(handsome_signal, dB=dB)
        save_and_compare(create_baseline, baseline_path, output_path,
                         filename, file_type, compare_output)

    # test if log_prefix and log_reference are working
    print(f"Testing: {function.__name__} (log parameters)")

    filename = function.__name__ + '_logParams'
    create_figure()
    function(handsome_signal, log_prefix=10, log_reference=.5, dB=True)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.freq), (plot.phase), (plot.group_delay)])
@pytest.mark.parametrize('xscale', [('log'), ('linear')])
def test_line_xscale_option(function, xscale, handsome_signal):
    """Test all line plots that have an xscale option."""
    # test if xscale option is working
    print(f"Testing: {function.__name__} (xscale={xscale})")

    filename = function.__name__ + '_xscale_' + xscale
    create_figure()
    function(handsome_signal, xscale=xscale)
    save_and_compare(create_baseline, baseline_path, output_path,
                     filename, file_type, compare_output)


def test_line_xscale_assertion(sine):
    """
    Test if all line plots raise an assertion for a wrong scale parameter.
    """

    with raises(ValueError):
        plot.freq(sine, xscale="warped")

    with raises(ValueError):
        plot.phase(sine, xscale="warped")

    with raises(ValueError):
        plot.group_delay(sine, xscale="warped")

    with raises(ValueError):
        plot.spectrogram(sine, yscale="warped")

    plt.close("all")


@pytest.mark.parametrize('function', [
    (plot.time), (plot.group_delay), (plot.spectrogram)])
@pytest.mark.parametrize('unit', [
    (None), ('s'), ('ms'), ('mus'), ('samples')])
def test_time_unit(function, unit, impulse_group_delay):
    """Test plottin with different units."""
    print(f"Testing: {function.__name__} (unit={unit})")

    filename = f'{function.__name__}_unit_{str(unit)}'
    create_figure()
    function(impulse_group_delay[0], unit=unit)
    save_and_compare(create_baseline, baseline_path, output_path,
                     filename, file_type, compare_output)


def test_time_unit_assertion(sine):
    """Test if all line plots raise an assertion for a wrong unit parameter."""

    with raises(ValueError):
        plot.time(sine, unit="pascal")

    with raises(ValueError):
        plot.group_delay(sine, unit="pascal")

    with raises(ValueError):
        plot.spectrogram(sine, unit="pascal")

    plt.close("all")


def test_line_custom_subplots(handsome_signal, handsome_signal_v2):
    """
    Test custom subplots in row, column, and mixed layout including hold
    functionality.
    """

    # plot layouts to be tested
    plots = {
        'row': [plot.time, plot.freq],
        'col': [[plot.time], [plot.freq]],
        'mix': [[plot.time, plot.freq],
                [plot.phase, plot.group_delay]]
    }

    for p in plots:
        print(f"Testing: {p}")

        # test initial plot
        filename = 'custom_subplots_' + p
        create_figure()
        plot.custom_subplots(handsome_signal, plots[p])
        save_and_compare(create_baseline, baseline_path, output_path, filename,
                         file_type, compare_output)

        # test hold functionality
        filename = 'custom_subplots_' + p + '_hold'
        plot.custom_subplots(handsome_signal_v2, plots[p])
        save_and_compare(create_baseline, baseline_path, output_path, filename,
                         file_type, compare_output)


def test_line_time_data(handsome_signal):
    """Test time data plot with default arguments."""
    function = plot.time
    time_data = pf.TimeData(handsome_signal.time, handsome_signal.times)
    print(f"Testing: {function.__name__}")

    filename = function.__name__ + 'time_data'
    create_figure()
    function(time_data)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.freq), (plot.phase), (plot.freq_phase)])
def test_line_frequency_data(function, handsome_signal):
    """Test frequency data plot with default arguments."""
    print(f"Testing: {function.__name__}")
    frequency_data = pf.FrequencyData(
        handsome_signal.freq, handsome_signal.frequencies)
    filename = function.__name__ + 'frequency_data'
    create_figure()
    function(frequency_data)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


def test_spectrogram():
    """Test spectrogram with default parameters"""
    function = plot.spectrogram

    print(f"Testing: {function.__name__}")

    filename = function.__name__ + '_default'
    create_figure()
    function(pf.signals.exponential_sweep_time(2**16, [100, 10e3]))
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.time_2d), (plot.freq_2d), (plot.phase_2d), (plot.group_delay_2d),
    (plot.time_freq_2d), (plot.freq_phase_2d), (plot.freq_group_delay_2d)])
def test_2d_plots(function, handsome_signal_2d):
    """Test all 2d plots with default arguments."""
    filename = function.__name__
    create_figure()
    function(handsome_signal_2d)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.time_2d), (plot.freq_2d), (plot.phase_2d),
    (plot.group_delay_2d), (plot.time_freq_2d), (plot.freq_phase_2d),
    (plot.freq_group_delay_2d)])
@pytest.mark.parametrize('points', [('default'), ('custom')])
@pytest.mark.parametrize('orientation', [('vertical'), ('horizontal')])
def test_2d_points_orientation(
        function, orientation, points, handsome_signal_2d):
    """Test 2D plots with varing `points` and `orientation` parameters"""
    print(f"Testing: {function.__name__}")
    points_label = 'points-default' if points == 'default' else 'points-custom'
    signal = handsome_signal_2d
    if points == 'custom':
        points = np.linspace(0, 360, np.prod(handsome_signal_2d.cshape))
    else:
        points = None
    filename = f'{function.__name__}_{orientation}_{points_label}'
    create_figure()
    function(signal, indices=points, orientation=orientation)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.spectrogram), (plot.time_2d), (plot.freq_2d), (plot.phase_2d),
    (plot.group_delay_2d)])
@pytest.mark.parametrize('colorbar', [('off'), ('axes')])
def test_2d_colorbar_options(function, colorbar, handsome_signal_2d):
    """Test 2D color bar options"""
    print(f"Testing: {function.__name__} with colorbar {colorbar}")
    filename = f'{function.__name__}_colorbar-{colorbar}'
    # pad zeros to get minimum signal length for spectrogram
    signal = handsome_signal_2d
    if function == plot.spectrogram:
        signal = pf.dsp.pad_zeros(signal, 2048 - signal.n_samples)
    fig = create_figure()
    if colorbar == "off":
        # test not plotting a colorbar
        function(signal, colorbar=False)
    elif colorbar == "axes":
        # test plotting colorbar to specified axis
        fig.clear()
        _, ax = plt.subplots(1, 2, num=fig.number)
        function(signal, ax=ax)
    save_and_compare(create_baseline, baseline_path, output_path,
                     filename, file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.spectrogram), (plot.time_2d), (plot.freq_2d), (plot.phase_2d),
    (plot.group_delay_2d)])
def test_2d_colorbar_assertion(function, handsome_signal_2d):
    """
    Test assertion when passing an array of axes but not having a colorbar.
    """
    with raises(ValueError, match="A list of axes"):
        function(handsome_signal_2d, colorbar=False,
                 ax=[plt.gca(), plt.gca()])


@pytest.mark.parametrize('function', [
    (plot.time_2d), (plot.freq_2d), (plot.phase_2d),
    (plot.group_delay_2d), (plot.time_freq_2d), (plot.freq_phase_2d),
    (plot.freq_group_delay_2d)])
def test_2d_cshape_assertion(function):
    """
    Test assertion when passing a signal with wrong cshape.
    """
    error_str = r"signal.cshape must be \(m, \) with m\>=2 but is \(2, 2\)"
    with raises(ValueError, match=error_str):
        function(pf.signals.impulse(10, [[0, 0], [0, 0]]))


@pytest.mark.parametrize('param', [
    (['phase_2d_deg', True, False]),
    (['phase_2d_unwrap', False, True]),
    (['phase_2d_deg_unwrap', True, True])])
def test_2d_phase_options(param, handsome_signal_2d):
    """Test parameters that are unique to the phase plot."""
    print(f"Testing: {param[0]}")

    filename = param[0]
    create_figure()
    plot.phase_2d(handsome_signal_2d, deg=param[1], unwrap=param[2])
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


def test_phase_2d_unwrap_assertion(handsome_signal_2d):
    """Test assertion for unwrap parameter."""
    with raises(ValueError):
        plot.phase_2d(handsome_signal_2d, unwrap='infinity')


@pytest.mark.parametrize('function', [
    (plot.time_2d), (plot.freq_2d)])
def test_2d_dB_option(function, handsome_signal_2d):
    """Test all 2d plots that have a dB option."""
    # test if dB option is working
    for dB in [True, False]:
        print(f"Testing: {function.__name__} (dB={dB})")

        filename = function.__name__ + '_dB_' + str(dB)
        create_figure()
        function(handsome_signal_2d, dB=dB)
        save_and_compare(create_baseline, baseline_path, output_path,
                         filename, file_type, compare_output)

    # test if log_prefix and log_reference are working
    print(f"Testing: {function.__name__} (log parameters)")

    filename = function.__name__ + '_logParams'
    create_figure()
    function(handsome_signal_2d, log_prefix=10, log_reference=.5, dB=True)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.freq_2d), (plot.phase_2d), (plot.group_delay_2d)])
@pytest.mark.parametrize('xscale', [('log'), ('linear')])
def test_2d_xscale_option(function, xscale, handsome_signal_2d):
    """Test all 2d plots that have an xscale option."""
    # test if xscale option is working
    print(f"Testing: {function.__name__} (xscale={xscale})")

    filename = function.__name__ + '_xscale_' + xscale
    create_figure()
    function(handsome_signal_2d, xscale=xscale)
    save_and_compare(create_baseline, baseline_path, output_path,
                     filename, file_type, compare_output)


def test_2d_xscale_assertion(handsome_signal_2d):
    """
    Test if all 2d plots raise an assertion for a wrong scale parameter.
    """

    with raises(ValueError):
        plot.freq(handsome_signal_2d, xscale="warped")

    with raises(ValueError):
        plot.phase(handsome_signal_2d, xscale="warped")

    with raises(ValueError):
        plot.group_delay(handsome_signal_2d, xscale="warped")

    with raises(ValueError):
        plot.spectrogram(handsome_signal_2d, yscale="warped")

    plt.close("all")


@pytest.mark.parametrize('function', [
    (plot.time_2d), (plot.group_delay_2d)])
@pytest.mark.parametrize('unit', [
    (None), ('s'), ('ms'), ('mus'), ('samples')])
def test_2d_time_unit(function, unit, handsome_signal_2d):
    """Test plottin with different units."""
    print(f"Testing: {function.__name__} (unit={unit})")

    filename = f'{function.__name__}_unit_{str(unit)}'
    create_figure()
    function(handsome_signal_2d, unit=unit)
    save_and_compare(create_baseline, baseline_path, output_path,
                     filename, file_type, compare_output)


def test_2d_time_unit_assertion(handsome_signal_2d):
    """Test if all 2d plots raise an assertion for a wrong unit parameter."""

    with raises(ValueError):
        plot.time_2d(handsome_signal_2d, unit="pascal")

    with raises(ValueError):
        plot.group_delay_2d(handsome_signal_2d, unit="pascal")

    plt.close("all")


def test_2d_time_data(handsome_signal_2d):
    """Test 2d time data plot with default arguments."""
    function = plot.time
    time_data = pf.TimeData(
        handsome_signal_2d.time, handsome_signal_2d.times)
    print(f"Testing: {function.__name__}")

    filename = function.__name__ + 'time_data'
    create_figure()
    function(time_data)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


@pytest.mark.parametrize('function', [
    (plot.freq), (plot.phase), (plot.freq_phase)])
def test_2d_frequency_data(handsome_signal, function):
    """Test 2d frequency data plot with default arguments."""
    frequency_data = pf.FrequencyData(
        handsome_signal.freq, handsome_signal.frequencies)
    print(f"Testing: {function.__name__}")

    filename = function.__name__ + 'frequency_data'
    create_figure()
    function(frequency_data)
    save_and_compare(create_baseline, baseline_path, output_path, filename,
                     file_type, compare_output)


def test_use():
    """Test if use changes the plot style."""

    for style in ["dark", "default"]:

        filename = 'use_' + style
        plot.utils.use(style)
        create_figure()
        plt.plot([1, 2, 3], [1, 2, 3])
        save_and_compare(create_baseline, baseline_path, output_path, filename,
                         file_type, compare_output)


def test_freq_fft_norm_dB(noise):
    """Test correct log_prefix in plot.freq depending on fft_norm."""
    create_figure()
    noise.fft_norm = 'power'
    ax = plot.freq(noise)
    y_actual = ax.lines[0].get_ydata().flatten()
    y_desired = 10*np.log10(np.abs(noise.freq)).flatten()
    npt.assert_allclose(y_actual, y_desired, atol=1e-6)

    create_figure()
    noise.fft_norm = 'psd'
    ax = plot.freq(noise)
    y_actual = ax.lines[0].get_ydata().flatten()
    y_desired = 10*np.log10(np.abs(noise.freq)).flatten()
    npt.assert_allclose(y_actual, y_desired, atol=1e-6)


def test_time_freq_fft_norm_dB(noise):
    """Test correct log_prefix in plot.time_freq depending on fft_norm."""
    create_figure()
    noise.fft_norm = 'power'
    ax = plot.time_freq(noise)
    y_actual = ax[1].lines[0].get_ydata().flatten()
    y_desired = 10*np.log10(np.abs(noise.freq)).flatten()
    npt.assert_allclose(y_actual, y_desired, atol=1e-6)

    create_figure()
    noise.fft_norm = 'psd'
    ax = plot.time_freq(noise)
    y_actual = ax[1].lines[0].get_ydata().flatten()
    y_desired = 10*np.log10(np.abs(noise.freq)).flatten()
    npt.assert_allclose(y_actual, y_desired, atol=1e-6)
