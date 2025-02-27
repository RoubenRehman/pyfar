"""Plotting functions for 2D data."""
import numpy as np
from pyfar.plot.utils import context
from pyfar import Signal
from . import _two_d
from . import _interaction as ia


def time_2d(signal, dB=False, log_prefix=None, log_reference=1, unit="s",
            indices=None, orientation="vertical", method='pcolormesh',
            colorbar=True, ax=None, style='light', mode='real', **kwargs):
    """
    2D color coded plot of time signals.

    Plots ``signal.time`` and passes keyword arguments (`kwargs`) to
    :py:func:`matplotlib.pyplot.pcolormesh` or
    :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal, TimeData
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    dB : bool
        Indicate if the data should be plotted in dB in which case
        ``log_prefix * np.log10(signal.time / log_reference)`` is used. The
        default is ``False``.
    log_prefix : integer, float
        Prefix for calculating the logarithmic frequency data. The default is
        ``None``, so ``10`` is chosen if ``signal.fft_norm`` is ``'power'`` or
        ``'psd'`` and ``20`` otherwise.
    log_reference : integer
        Reference for calculating the logarithmic time data. The default is
        ``1``.
    unit : str, None
        Set the unit of the time axis.

        ``'s'`` (default)
            seconds
        ``'ms'``
            milliseconds
        ``'mus'``
            microseconds
        ``'samples'``
            samples
        ``'auto'``
            Use seconds, milliseconds, or microseconds depending on the length
            of the data.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``ax``
            If a single axis is passed, this is used for plotting. If
            `colorbar` is ``True`` the space for the colorbar is taken from
            this axis.
        ``[ax, ax]``
            If a list or array of two axes is passed, the first is used to plot
            the data and the second to plot the colorbar. In this case
            `colorbar` must be ``True``.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    mode : str, optional
        ``real``, ``imag``, or ``abs`` to specify if the real part, imaginary
        part or absolute value of the time data is plotted. ``'imag'`` and
        ``'abs'``` can only be used for complex Signals.
        The default is ``real``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.


    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of two axes is returned. The first
        is the axis on which the data is plotted, the second is the axis of the
        colorbar. If `colorbar` is ``False``, only the axis on which the data
        is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can be
        used to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Examples
    --------
    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     64, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.time_2d(impulses, unit='ms')
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._time_2d(
            signal, dB, log_prefix, log_reference, unit,
            indices, orientation, method, colorbar, ax, mode, **kwargs)

    plot_parameter = ia.PlotParameter(
        'time_2d', dB_time=dB, log_prefix_time=log_prefix,
        log_reference=log_reference, unit_time=unit, indices=indices,
        orientation=orientation, method=method, colorbar=colorbar, mode=mode)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax.interaction = interaction

    if colorbar:
        ax = [ax, cb.ax]

    return ax, qm, cb


def freq_2d(signal, dB=True, log_prefix=None, log_reference=1,
            freq_scale='log', indices=None, orientation="vertical",
            method='pcolormesh', colorbar=True, ax=None, style='light',
            side='right', **kwargs):
    """
    2D color coded plot of magnitude spectra.

    Plots ``abs(signal.freq)`` and passes keyword arguments (`kwargs`) to
    :py:func:`matplotlib.pyplot.pcolormesh` or
    :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal, FrequencyData
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    dB : bool
        Indicate if the data should be plotted in dB in which case
        ``log_prefix * np.log10(abs(signal.freq) / log_reference)`` is used.
        The default is ``True``.
    log_prefix : integer, float
        Prefix for calculating the logarithmic frequency data. The default is
        ``None``, so ``10`` is chosen if ``signal.fft_norm`` is ``'power'`` or
        ``'psd'`` and ``20`` otherwise.
    log_reference : integer, float
        Reference for calculating the logarithmic frequency data. The default
        is ``1``.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``log``.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``ax``
            If a single axis is passed, this is used for plotting. If
            `colorbar` is ``True`` the space for the colorbar is taken from
            this axis.
        ``[ax, ax]``
            If a list or array of two axes is passed, the first is used to plot
            the data and the second to plot the colorbar. In this case
            `colorbar` must be ``True``.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.

    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of two axes is returned. The first
        is the axis on which the data is plotted, the second is the axis of the
        colorbar. If `colorbar` is ``False``, only the axis on which the data
        is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can be
        used to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Example
    -------

    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     2048, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.freq_2d(impulses, dB=False)
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._freq_2d(
            signal, dB, log_prefix, log_reference, freq_scale, indices,
            orientation, method, colorbar, ax, side, **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'freq_2d', dB_freq=dB, log_prefix_freq=log_prefix,
        log_reference=log_reference, xscale=freq_scale, indices=indices,
        orientation=orientation, method=method, colorbar=colorbar, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax.interaction = interaction

    if colorbar:
        ax = [ax, cb.ax]

    return ax, qm, cb


def phase_2d(signal, deg=False, unwrap=False, freq_scale='log', indices=None,
             orientation="vertical", method='pcolormesh',
             colorbar=True, ax=None, style='light', side='right', **kwargs):
    """
    2D color coded plot of phase spectra.

    Plots ``angle(signal.freq)`` and passes keyword arguments (`kwargs`) to
    :py:func:`matplotlib.pyplot.pcolormesh` or
    :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal, FrequencyData
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    deg : bool
        Plot the phase in degrees. The default is ``False``, which plots the
        phase in radians.
    unwrap : bool, str
        True to unwrap the phase or ``'360'`` to unwrap the phase to 2 pi. The
        default is ``False``, which plots the wrapped phase.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``log``.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``ax``
            If a single axis is passed, this is used for plotting. If
            `colorbar` is ``True`` the space for the colorbar is taken from
            this axis.
        ``[ax, ax]``
            If a list or array of two axes is passed, the first is used to plot
            the data and the second to plot the colorbar. In this case
            `colorbar` must be ``True``.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.

    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of two axes is returned. The first
        is the axis on which the data is plotted, the second is the axis of the
        colorbar. If `colorbar` is ``False``, only the axis on which the data
        is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can be
        used to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Example
    -------

    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     2048, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.phase_2d(impulses, unwrap=True, freq_scale="linear")
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._phase_2d(
            signal, deg, unwrap, freq_scale, indices, orientation, method,
            colorbar, ax, side, **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'phase_2d', deg=deg, unwrap=unwrap, xscale=freq_scale, indices=indices,
        orientation=orientation, method=method, colorbar=colorbar, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax.interaction = interaction

    if colorbar:
        ax = [ax, cb.ax]

    return ax, qm, cb


def group_delay_2d(signal, unit="s", freq_scale='log', indices=None,
                   orientation="vertical", method='pcolormesh',
                   colorbar=True, ax=None, style='light', side='right',
                   **kwargs):
    """
    2D color coded plot of the group delay.

    Plots ``pyfar.dsp.group_delay(signal.freq)`` and passes keyword arguments
    (`kwargs`) to :py:func:`matplotlib.pyplot.pcolormesh` or
    :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    unit : str, None
        Set the unit of the time axis.

        ``'s'`` (default)
            seconds
        ``'ms'``
            milliseconds
        ``'mus'``
            microseconds
        ``'samples'``
            samples
        ``'auto'``
            Use seconds, milliseconds, or microseconds depending on the length
            of the data.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``log``.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``ax``
            If a single axis is passed, this is used for plotting. If
            `colorbar` is ``True`` the space for the colorbar is taken from
            this axis.
        ``[ax, ax]``
            If a list or array of two axes is passed, the first is used to plot
            the data and the second to plot the colorbar. In this case
            `colorbar` must be ``True``.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.

    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of four axes is returned. The first
        two are the axis on which the data is plotted, the last two are the
        axis of the colorbar. If `colorbar` is ``False``, only the axes on
        which the data is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can b
        used to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Example
    -------

    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     2048, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.group_delay_2d(impulses, unit="samples")
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._group_delay_2d(
            signal, unit, freq_scale, indices, orientation, method,
            colorbar, ax, side, **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'group_delay_2d', unit_gd=unit, xscale=freq_scale, indices=indices,
        orientation=orientation, method=method, colorbar=colorbar, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax.interaction = interaction

    if colorbar:
        ax = [ax, cb.ax]

    return ax, qm, cb


def time_freq_2d(signal, dB_time=False, dB_freq=True, log_prefix_time=20,
                 log_prefix_freq=None, log_reference=1, freq_scale='log',
                 unit='s', indices=None, orientation="vertical",
                 method='pcolormesh', colorbar=True, ax=None, style='light',
                 mode='real', side='right', **kwargs):
    """
    2D color coded plot of time signals and magnitude spectra (2 by 1 subplot).

    Plots ``signal.time`` and ``abs(signal.freq)`` passes keyword arguments
    (`kwargs`) to :py:func:`matplotlib.pyplot.pcolormesh` or
    :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    dB_time : bool
        Indicate if the data should be plotted in dB in which case
        ``log_prefix * np.log10(signal.time / log_reference)`` is used. The
        default is ``False``.
    dB_freq : bool
        Indicate if the data should be plotted in dB in which case
        ``log_prefix * np.log10(abs(signal.freq) / log_reference)`` is used.
        The default is ``True``.
    log_prefix_time : integer, float
        Prefix for calculating the logarithmic time data.
        The default is ``20``.
    log_prefix_freq : integer, float
        Prefix for calculating the logarithmic frequency data. The default is
        ``None``, so ``10`` is chosen if ``signal.fft_norm`` is ``'power'`` or
        ``'psd'`` and ``20`` otherwise.
    log_reference : integer
        Reference for calculating the logarithmic time/frequency data.
        The default is ``1``.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``log``.
    unit : str, None
        Set the unit of the time axis.

        ``'s'`` (default)
            seconds
        ``'ms'``
            milliseconds
        ``'mus'``
            microseconds
        ``'samples'``
            samples
        ``'auto'``
            Use seconds, milliseconds, or microseconds depending on the length
            of the data.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``[ax, ax]``
            Two axes to plot on. Space for the colorbar of each plot is taken
            from the provided axes.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    mode : str
        ``real``, ``imag``, or ``abs`` to specify if the real part, imaginary
        part or absolute value of a complex-valued time domain signal is
        plotted. The default is ``real``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.


    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of four axes is returned. The first
        two are the axis on which the data is plotted, the last two are the
        axis of the colorbar. If `colorbar` is ``False``, only the axes on
        which the data is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can be
        used to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Examples
    --------
    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     64, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.time_freq_2d(impulses, dB_freq=False, unit='ms')
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._time_freq_2d(
            signal, dB_time, dB_freq, log_prefix_time, log_prefix_freq,
            log_reference, freq_scale, unit, indices, orientation, method,
            colorbar, ax, mode, side, **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'time_freq_2d', dB_time=dB_time, dB_freq=dB_freq,
        log_prefix_time=log_prefix_time, log_prefix_freq=log_prefix_freq,
        log_reference=log_reference, xscale=freq_scale, unit_time=unit,
        indices=indices, orientation=orientation, method=method,
        colorbar=colorbar, mode=mode, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax[0].interaction = interaction

    if colorbar:
        ax = np.append(ax, [cb[0].ax, cb[1].ax])

    return ax, qm, cb


def freq_phase_2d(signal, dB=True, log_prefix=None, log_reference=1,
                  freq_scale='log', deg=False, unwrap=False, indices=None,
                  orientation="vertical", method='pcolormesh',
                  colorbar=True, ax=None, style='light', side='right',
                  **kwargs):
    """
    2D color coded plot of magnitude and phase spectra (2 by 1 subplot).

    Plots ``abs(signal.freq)`` and ``angle(signal.freq)`` and passes keyword
    arguments (`kwargs`) to :py:func:`matplotlib.pyplot.pcolormesh` or
    :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal, FrequencyData
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    dB : bool
        Indicate if the data should be plotted in dB in which case
        ``log_prefix * np.log10(abs(signal.freq) / log_reference)`` is used.
        The default is ``True``.
    log_prefix : integer, float
        Prefix for calculating the logarithmic frequency data. The default is
        ``None``, so ``10`` is chosen if ``signal.fft_norm`` is ``'power'`` or
        ``'psd'`` and ``20`` otherwise.
    log_reference : integer
        Reference for calculating the logarithmic frequency data. The default
        is ``1``.
    deg : bool
        Flag to plot the phase in degrees. The default is ``False``.
    unwrap : bool, str
        True to unwrap the phase or ``'360'`` to unwrap the phase to 2 pi. The
        default is ``False``.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``log``.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``[ax, ax]``
            Two axes to plot on. Space for the colorbar of each plot is taken
            from the provided axes.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.


    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of four axes is returned. The first
        two are the axis on which the data is plotted, the last two are the
        axis of the colorbar. If `colorbar` is ``False``, only the axes on
        which the data is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can be used
        to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Examples
    --------
    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     2048, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.freq_phase_2d(impulses, dB=False, unwrap=True,
        ...                       freq_scale="linear")
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._freq_phase_2d(
            signal, dB, log_prefix, log_reference, freq_scale, deg, unwrap,
            indices, orientation, method, colorbar, ax, side, **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'freq_phase_2d', dB_freq=dB, log_prefix_freq=log_prefix,
        log_reference=log_reference, xscale=freq_scale, deg=deg, unwrap=unwrap,
        indices=indices, orientation=orientation, method=method,
        colorbar=colorbar, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax[0].interaction = interaction

    if colorbar:
        ax = np.append(ax, [cb[0].ax, cb[1].ax])

    return ax, qm, cb


def freq_group_delay_2d(signal, dB=True, log_prefix=None, log_reference=1,
                        unit="s", freq_scale='log', indices=None,
                        orientation="vertical", method='pcolormesh',
                        colorbar=True, ax=None, style='light', side='right',
                        **kwargs):
    """
    2D color coded plot of magnitude spectra and group delay (2 by 1 subplot).

    Plots ``abs(signal.freq)`` and ``pyfar.dsp.group_delay(signal.freq)`` and
    passes keyword arguments (`kwargs`) to
    :py:func:`matplotlib.pyplot.pcolormesh`
    or :py:func:`matplotlib.pyplot.contourf`.

    Parameters
    ----------
    signal : Signal
        The input data to be plotted. `signal.cshape` must be `(m, )` with
        `m>1`.
    dB : bool
        Flag to plot the logarithmic magnitude spectrum. The default is
        ``True``.
    log_prefix : integer, float
        Prefix for calculating the logarithmic frequency data. The default is
        ``None``, so ``10`` is chosen if ``signal.fft_norm`` is ``'power'`` or
        ``'psd'`` and ``20`` otherwise.
    log_reference : integer
        Reference for calculating the logarithmic frequency data. The default
        is ``1``.
    unit : str, None
        Set the unit of the time axis.

        ``'s'`` (default)
            seconds
        ``'ms'``
            milliseconds
        ``'mus'``
            microseconds
        ``'samples'``
            samples
        ``'auto'``
            Use seconds, milliseconds, or microseconds depending on the length
            of the data.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``log``.
    indices: array like, optional
        Points at which the channels of `signal` were sampled (e.g. azimuth
        angles or x values). `indices` must be monotonously increasing/
        decreasing and have as many entries as `signal` has channels. The
        default is ``'None'`` which labels the N channels in `signal` from
        0 to N-1.
    orientation: string, optional
        ``'vertical'``
            The channels of `signal` will be plotted as as vertical lines.
        ``'horizontal'``
            The channels of `signal` will be plotted as horizontal lines.

        The default is ``'vertical'``
    method: string, optional
        The Matplotlib plotting method.

        ``'pcolormesh'``
            Create a pseudocolor plot with a non-regular rectangular grid.
            The resolution of the data is clearly visible.
        ``'contourf'``
            Create a filled contour plot. The data is smoothly interpolated,
            which might mask the data's resolution.

        The default is ``'pcolormesh'``.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``[ax, ax]``
            Two axes to plot on. Space for the colorbar of each plot is taken
            from the provided axes.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.


    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of four axes is returned. The first
        two are the axis on which the data is plotted, the last two are the
        axis of the colorbar. If `colorbar` is ``False``, only the axes on
        which the data is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh` /
        :py:class:`matplotlib.contour.QuadContourSet` collection. This can be
        used to manipulate the way the data is displayed, e.g., by limiting the
        range of the colormap by ``quad_mesh.set_clim()``. It can also be used
        to generate a colorbar by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Examples
    --------
    Plot a 25-channel impulse signal with different delays and amplitudes.

    .. plot::

        >>> import pyfar as pf
        >>> import numpy as np
        >>> impulses = pf.signals.impulse(
        ...     2048, np.arange(0, 25), np.linspace(1, .5, 25))
        >>> pf.plot.freq_group_delay_2d(impulses, dB=False, unit="samples")
    """  # noqa: E501

    with context(style):
        ax, qm, cb = _two_d._freq_group_delay_2d(
            signal, dB, log_prefix, log_reference, unit, freq_scale, indices,
            orientation, method, colorbar, ax, side, **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'freq_group_delay_2d', dB_freq=dB, log_prefix_freq=log_prefix,
        log_reference=log_reference, xscale=freq_scale, unit_gd=unit,
        indices=indices, orientation=orientation, method=method,
        colorbar=colorbar, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax[0].interaction = interaction

    if colorbar:
        ax = np.append(ax, [cb[0].ax, cb[1].ax])

    return ax, qm, cb


def spectrogram(signal, dB=True, log_prefix=None, log_reference=1,
                freq_scale='linear', unit='s', window='hann',
                window_length=1024, window_overlap_fct=0.5,
                colorbar=True, ax=None, style='light', side='right',
                **kwargs):
    """Plot blocks of the magnitude spectrum versus time.

    Parameters
    ----------
    signal : Signal
        The input data to be plotted. Multidimensional data are flattened for
        plotting, e.g, a signal of ``signal.cshape = (2, 2)`` would be plotted
        in the order ``(0, 0)``, ``(0, 1)``, ``(1, 0)``, ``(1, 1)``.
    dB : bool
        Indicate if the data should be plotted in dB in which case
        ``log_prefix * np.log10(abs(signal.freq) / log_reference)`` is used.
        The default is ``True``.
    log_prefix : integer, float
        Prefix for calculating the logarithmic frequency data. The default is
        ``None``, so ``10`` is chosen if ``signal.fft_norm`` is ``'power'`` or
        ``'psd'`` and ``20`` otherwise.
    log_reference : integer
        Reference for calculating the logarithmic frequency data. The default
        is ``1``.
    freq_scale : str
        ``linear`` or ``log`` to plot on a linear or logarithmic frequency
        axis. The default is ``linear``.
    unit : str, None
        Set the unit of the time axis.

        ``'s'`` (default)
            seconds
        ``'ms'``
            milliseconds
        ``'mus'``
            microseconds
        ``'samples'``
            samples
        ``'auto'``
            Use seconds, milliseconds, or microseconds depending on the length
            of the data.
    window : str
        Specifies the window that is applied to each block of the time data
        before applying the Fourier transform. The default is ``hann``. See
        :py:func:`scipy.signal.get_window` for a list of possible windows.
    window_length : integer
        Specifies the window/block length in samples. The default is ``1024``.
    window_overlap_fct : double
        Ratio of indices to overlap between blocks [0...1]. The default is
        ``0.5``, which would result in 512 samples overlap for a window length
        of 1024 samples.
    colorbar : bool, optional
        Control the colorbar. The default is ``True``, which adds a colorbar
        to the plot. ``False`` omits the colorbar.
    ax : matplotlib.axes.Axes
        Axes to plot on.

        ``None``
            Use the current axis, or create a new axis (and figure) if there is
            none.
        ``ax``
            If a single axis is passed, this is used for plotting. If
            `colorbar` is ``True`` the space for the colorbar is taken from
            this axis.
        ``[ax, ax]``
            If a list or array of two axes is passed, the first is used to plot
            the data and the second to plot the colorbar. In this case
            `colorbar` must be ``True``.

        The default is ``None``.
    style : str
        ``light`` or ``dark`` to use the pyfar plot styles or a plot style from
        :py:data:`matplotlib.style.available`. Pass a dictionary to set
        specific plot parameters, for example
        ``style = {'axes.facecolor':'black'}``. Pass an empty dictionary
        ``style = {}`` to use the currently active plotstyle. The default is
        ``light``.
    side : str, optional
        ``'right'`` to plot the right-sided spectrum containing the positive
        frequencies, or ``'left'`` to plot the left-sided spectrum containing
        the negative frequencies (only possible for complex Signals). The
        default is ``'right'``.
    **kwargs
        Keyword arguments that are passed to
        :py:func:`matplotlib.pyplot.pcolormesh` or
        :py:func:`matplotlib.pyplot.contourf`.

    Returns
    -------
    ax : matplotlib.axes.Axes
        If `colorbar` is ``True`` an array of two axes is returned. The first
        is the axis on which the data is plotted, the second is the axis of the
        colorbar. If `colorbar` is ``False``, only the axis on which the data
        is plotted is returned.
    quad_mesh : :py:class:`~matplotlib.collections.QuadMesh`, :py:class:`matplotlib.contour.QuadContourSet`
        The Matplotlib :py:class:`~matplotlib.collections.QuadMesh`
        collection. This can be used to manipulate the
        way the data is displayed, e.g., by limiting the range of the colormap
        by ``quad_mesh.set_clim()``. It can also be used to generate a colorbar
        by ``cb = fig.colorbar(quad_mesh, ...)``.
    colorbar : Colorbar
        The Matplotlib colorbar object if `colorbar` is ``True`` and ``None``
        otherwise. This can be used to control the appearance of the colorbar,
        e.g., the label can be set by ``colorbar.set_label()``.

    Example
    -------

    Plot the spectrogram of a linear sweep

    .. plot::

        >>> import pyfar as pf
        >>> sweep = pf.signals.linear_sweep_time(2**14, [0, 22050])
        >>> pf.plot.spectrogram(sweep, unit='ms')
    """  # noqa: E501
    if not isinstance(signal, Signal):
        raise TypeError('Input data has to be of type: Signal.')

    with context(style):
        ax, qm, cb = _two_d._spectrogram(
            signal.flatten(), dB, log_prefix, log_reference, freq_scale, unit,
            window, window_length, window_overlap_fct, colorbar, ax, side,
            **kwargs)

    # manage interaction
    plot_parameter = ia.PlotParameter(
        'spectrogram', dB_freq=dB, log_prefix_freq=log_prefix,
        log_reference=log_reference, yscale=freq_scale, unit_time=unit,
        window=window, window_length=window_length,
        window_overlap_fct=window_overlap_fct, side=side)
    interaction = ia.Interaction(
        signal, ax, cb, style, plot_parameter, **kwargs)
    ax.interaction = interaction

    if colorbar:
        ax = [ax, cb.ax]

    return ax, qm, cb
