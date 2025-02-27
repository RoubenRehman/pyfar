"""Utilities for the pyfar plot module."""
import matplotlib.style as mpl_style
import os
import json
import contextlib
from . import _utils
from pyfar.plot._interaction import PlotParameter


def plotstyle(style='light'):
    """
    Get the fullpath of the pyfar plotstyles ``light`` or ``dark``.

    The plotstyles are defined by mplstyle files, which is Matplotlibs format
    to define styles. By default, pyfar uses the ``light`` plotstyle.

    Parameters
    ----------
    style : str
        ``light`` or ``dark``

    Returns
    -------
    style : str
        Full path to the pyfar plotstyle.

    See Also
    --------
    pyfar.plot.use
    pyfar.plot.context

    """

    if style in ['light', 'dark']:
        style = os.path.join(
            os.path.dirname(__file__), 'plotstyles', f'{style}.mplstyle')

    return style


@contextlib.contextmanager
def context(style='light', after_reset=False):
    """Context manager for using plot styles temporarily.

    This context manager supports the two pyfar styles ``light`` and ``dark``.
    It is a wrapper for :py:func:`matplotlib.style.context`.

    Parameters
    ----------
    style : str, dict, Path or list
        A style specification. Valid options are:

        +------+-------------------------------------------------------------+
        | str  | The name of a style or a path/URL to a style file. For a    |
        |      | list of available style names, see                          |
        |      | :py:data:`matplotlib.style.available`.                      |
        +------+-------------------------------------------------------------+
        | dict | Dictionary with valid key/value pairs for                   |
        |      | :py:data:`matplotlib.rcParams`.                             |
        +------+-------------------------------------------------------------+
        | Path | A path-like object which is a path to a style file.         |
        +------+-------------------------------------------------------------+
        | list | A list of style specifiers (str, Path or dict) applied from |
        |      | first to last in the list.                                  |
        +------+-------------------------------------------------------------+

    after_reset : bool
        If ``True``, apply style after resetting settings to their defaults;
        otherwise, apply style on top of the current settings.

    See Also
    --------
    pyfar.plot.plotstyle

    Examples
    --------
    Generate customizable subplots with the default pyfar plot style

    >>> import pyfar as pf
    >>> import matplotlib.pyplot as plt
    >>> with pf.plot.context():
    >>>     fig, ax = plt.subplots(2, 1)
    >>>     pf.plot.time(pf.Signal([0, 1, 0, -1], 44100), ax=ax[0])
    """

    # get pyfar plotstyle if desired
    style = plotstyle(style)

    # apply plot style
    with mpl_style.context(style, after_reset=after_reset):
        yield


def use(style="light"):
    """
    Use plot style settings from a style specification.

    The style name of ``default`` is reserved for reverting back to
    the default style settings. This is a wrapper for
    :py:func:`matplotlib.style.use` that supports the pyfar plot styles
    ``light`` and ``dark``.

    Parameters
    ----------
    style : str, dict, Path or list
        A style specification. Valid options are:

        +------+-------------------------------------------------------------+
        | str  | The name of a style or a path/URL to a style file. For a    |
        |      | list of available style names, see                          |
        |      | :py:data:`matplotlib.style.available`.                      |
        +------+-------------------------------------------------------------+
        | dict | Dictionary with valid key/value pairs for                   |
        |      | :py:data:`matplotlib.rcParams`.                             |
        +------+-------------------------------------------------------------+
        | Path | A path-like object which is a path to a style file.         |
        +------+-------------------------------------------------------------+
        | list | A list of style specifiers (str, Path or dict) applied from |
        |      | first to last in the list.                                  |
        +------+-------------------------------------------------------------+

    See Also
    --------
    pyfar.plot.plotstyle

    Notes
    -----
    This updates the `rcParams` with the settings from the style. `rcParams`
    not defined in the style are kept.

    Examples
    --------
    Permanently use the pyfar default plot style

    >>> import pyfar as pf
    >>> import matplotlib.pyplot as plt
    >>> pf.plot.utils.use()
    >>> fig, ax = plt.subplots(2, 1)
    >>> pf.plot.time(pf.Signal([0, 1, 0, -1], 44100), ax=ax[0])

    """

    # get pyfar plotstyle if desired
    style = plotstyle(style)
    # use plot style
    mpl_style.use(style)


def color(color):
    """Return pyfar default color as HEX string.

    Parameters
    ----------
    color : int, str
        The colors can be specified by their index, their full name,
        or the first letter. Available colors are:

        +---+---------+-------------+
        | 1 | ``'b'`` | blue        |
        +---+---------+-------------+
        | 2 | ``'r'`` | red         |
        +---+---------+-------------+
        | 3 | ``'y'`` | yellow      |
        +---+---------+-------------+
        | 4 | ``'p'`` | purple      |
        +---+---------+-------------+
        | 5 | ``'g'`` | green       |
        +---+---------+-------------+
        | 6 | ``'t'`` | turquois    |
        +---+---------+-------------+
        | 7 | ``'o'`` | orange      |
        +---+---------+-------------+
        | 8 | ``'l'`` | light green |
        +---+---------+-------------+

    Returns
    -------
    color_hex : str
        pyfar default color as HEX string
    """
    color_dict = _utils._default_color_dict()
    colors = list(color_dict.keys())
    if isinstance(color, str):
        if color[0] not in colors:
            raise ValueError((f"color is '{color}' but must be one of the "
                              f"following {', '.join(colors)}"))
        else:
            # all colors differ by their first letter
            color_hex = color_dict[color[0]]
    elif isinstance(color, int):
        color_hex = list(color_dict.values())[color % len(colors)]
    else:
        raise ValueError("color is has to be of type str or int.")
    return color_hex


def shortcuts(show=True, report=False, layout="console"):
    """Show and return keyboard shortcuts for interactive figures.

    Note that the shortcuts are only available if using an interactive
    `Matplotlib backend
    <https://matplotlib.org/stable/users/explain/backends.html>`_

    .. include:: ../../docs/resources/plot_shortcuts.rst

    Parameters
    ----------
    show : bool, optional
        Output the keyboard shortcuts to the default console. The default is
        ``True``.
    report : bool, optional
        Return the console output as a string. The default is ``False``.
    layout : str, optional
        Specify the layout of the output. ``'console'`` for printing to console
        and ``'sphinx'`` for generating sphinx readable output. The default is
        ``'console'``.

    Returns
    -------
    short_cuts : dict
        Dictionary that contains all the shortcuts.
    output : str, optional
        The console output as a string. Only returned if `report` is ``True``.

    """  # noqa: W605 (to ignore \*)

    # load short cuts from json file
    sc = os.path.join(os.path.dirname(__file__), 'shortcuts', 'shortcuts.json')
    with open(sc, "r") as read_file:
        short_cuts = json.load(read_file)

    # print list of short cuts
    if show or report:
        # get list of plots that allow toggling axes and colormaps
        x_toggle = []
        y_toggle = []
        for plot in short_cuts["plots"]:
            params = PlotParameter(plot)
            if params.x_type is not None:
                if len(params.x_type) > 1:
                    x_toggle.append(plot)
            if params.y_type is not None:
                if len(params.y_type) > 1:
                    y_toggle.append(plot)

        # shortcuts for toggling between plots
        if layout == "console":
            sc_str = ("Use these shortcuts to toggle between plots\n"
                      "-------------------------------------------\n")
        elif layout == "sphinx":
            sc_str = "**Use these shortcuts to toggle between plots**\n\n"
            sc_str += (
                ".. list-table::\n"
                "   :widths: 25 100\n"
                "   :header-rows: 1\n\n"
                "   * - Key\n"
                "     - Plot\n")
        else:
            raise ValueError(
                f"layout is '{layout}' but must be 'console' or 'sphinx'")

        plt = short_cuts["plots"]
        for p in plt:
            if "key_verbose" in plt[p]:
                key = plt[p]["key_verbose"]
            else:
                key = plt[p]["key"]

            if layout == "console":
                sc_str += f'{", ".join(key)}: {p}\n'
            else:
                sc_str += (f'   * - {", ".join(key)}\n'
                           f'     - :py:func:`~pyfar.plot.{p}`\n')

        sc_str += ("\nNote that not all plots are available for TimeData and "
                   "FrequencyData objects as detailed in the "
                   ":py:mod:`plot module <pyfar.plot>` documentation.\n\n")

        # shortcut for controlling the plot
        if layout == "console":
            sc_str += ("Use these shortcuts to control the plot\n"
                       "---------------------------------------\n")
        elif layout == "sphinx":
            sc_str += "**Use these shortcuts to control the plot**\n\n"
            sc_str += (
                ".. list-table::\n"
                "   :widths: 25 100\n"
                "   :header-rows: 1\n\n"
                "   * - Key\n"
                "     - Action\n")

        ctr = short_cuts["controls"]
        for action in ctr:
            if "key_verbose" in ctr[action]:
                key = ctr[action]["key_verbose"]
            else:
                key = ctr[action]["key"]

            if layout == "console":
                sc_str += f'{", ".join(key)}: {ctr[action]["info"]}\n'
            else:
                sc_str += (f'   * - {", ".join(key)}\n'
                           f'     - {ctr[action]["info"]}\n')

        # notes on plot controls
        if layout == "console":
            sc_str += ("\nNotes on plot controls\n"
                       "----------------------\n")
        elif layout == "sphinx":
            sc_str += "\n**Notes on plot controls**\n\n"

        # generate links to plot function for sphinx documentation
        if layout == 'sphinx':
            x_toggle = [f":py:func:`~pyfar.plot.{x}`" for x in x_toggle]
            y_toggle = [f":py:func:`~pyfar.plot.{y}`" for y in y_toggle]
            spectrogram = ":py:func:`~pyfar.plot.spectrogram`"
        else:
            spectrogram = "spectrogram"

        sc_str += ("- Moving and zooming the x and y axes is supported by all "
                   "plots.\n"
                   "- Moving and zooming the colormap is only supported by "
                   "plots that have a colormap.\n"
                   "- Toggling the x-axis, y-axis and colormap toggles "
                   "between\n\n"
                   "  - linear and logarithmic axis scaling for frequency "
                   "axes,\n"
                   "  - seconds, milliseconds, microseconds, and samples for "
                   "time axes,\n"
                   "  - linear amplitude and amplitude in dB for axes showing "
                   "amplitudes,\n"
                   "  - wrapped and unwrapped phase for axes showing phase "
                   "phase information.\n\n"
                   "- Toggling the x-axis style is supported by: "
                   f"{', '.join(x_toggle)} (and their 2d versions)\n"
                   "- Toggling the y-axis style is supported by: "
                   f"{', '.join(y_toggle)} (and their 2d versions)\n"
                   "- Toggling the colormap style is supported by all "
                   "2d plots\n"
                   "- Toggling between line and 2D plots is not supported by:"
                   f" {spectrogram}\n")

    if show:
        print(sc_str)

    if report:
        return short_cuts, sc_str
    else:
        return short_cuts
