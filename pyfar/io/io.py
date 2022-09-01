"""
Read and write objects to disk, read and write audio files, read SOFA files.

The functions :py:func:`read` and :py:func:`write` allow to save or load
several pyfar objects and other variables. So, e.g., workspaces in notebooks
can be stored. :py:class:`Signal <pyfar.signal.Signal>` objects can be
imported and exported as WAV files using :py:func:`read_wav` and
:py:func:`write_wav`. :py:func:`read_sofa` provides functionality to read the
data stored in a SOFA file.
"""
import os.path
import pathlib

import warnings
import sofar as sf
import zipfile
import io
import soundfile
import tempfile
import numpy as np
import re

import pyfar
from pyfar import Signal, FrequencyData, Coordinates, TimeData
from . import _codec as codec
import pyfar.classes.filter as fo


def read_sofa(filename, verify=True):
    """
    Import a SOFA file as pyfar object.

    Parameters
    ----------
    filename : string, Path
        Input SOFA file (cf. [#]_, [#]_).
    verify : bool, optional
        Verify if the data contained in the SOFA file agrees with the AES69
        standard (see references). If the verification fails, the SOFA file
        can be loaded by setting ``verify=False``. The default is ``True``

    Returns
    -------
    audio : pyfar audio object
        The audio object that is returned depends on the DataType of the SOFA
        object:

        - :py:class:`~pyfar.classes.audio.Signal`
            A Signal object is returned is the DataType is ``'FIR'``,
            ``'FIR-E'``, or ``'FIRE'``.
        - :py:class:`~pyfar.classes.audio.FrequencyData`
            A FrequencyData object is returned is the DataType is ``'TF'``,
            ``'TF-E'``, or ``'TFE'``.

        The `cshape` of the object is is ``(M, R)`` with `M` being the number
        of measurements and `R` being the number of receivers from the SOFA
        file.
    source_coordinates : Coordinates
        Coordinates object containing the data stored in
        `SOFA_object.SourcePosition`. The domain, convention and unit are
        automatically matched.
    receiver_coordinates : Coordinates
        Coordinates object containing the data stored in
        `SOFA_object.RecevierPosition`. The domain, convention and unit are
        automatically matched.

    Notes
    -----
    * This function uses the sofar package to read SOFA files [#]_.

    References
    ----------
    .. [#] https://www.sofaconventions.org
    .. [#] “AES69-2020: AES Standard for File Exchange-Spatial Acoustic Data
        File Format.”, 2020.
    .. [#] https://pyfar.org

    """

    sofa = sf.read_sofa(filename, verify)
    return convert_sofa(sofa)


def convert_sofa(sofa):
    """
    Convert SOFA object to pyfar object.

    Parameters
    ----------
    sofa : SOFA object
        A SOFA object read or generated by the sofar package ([#]_).

    Returns
    -------
    audio : pyfar audio object
        The audio object that is returned depends on the DataType of the SOFA
        object:

        - :py:class:`~pyfar.classes.audio.Signal`
            A Signal object is returned is the DataType is ``'FIR'``,
            ``'FIR-E'``, or ``'FIRE'``.
        - :py:class:`~pyfar.classes.audio.FrequencyData`
            A FrequencyData object is returned is the DataType is ``'TF'``,
            ``'TF-E'``, or ``'TFE'``.

        The `cshape` of the object is is ``(M, R)`` with `M` being the number
        of measurements and `R` being the number of receivers from the SOFA
        file.
    source_coordinates : Coordinates
        Coordinates object containing the data stored in
        `SOFA_object.SourcePosition`. The domain, convention and unit are
        automatically matched.
    receiver_coordinates : Coordinates
        Coordinates object containing the data stored in
        `SOFA_object.RecevierPosition`. The domain, convention and unit are
        automatically matched.

    References
    ----------
    .. [#] https://pyfar.org
    """

    # check input
    if not isinstance(sofa, sf.Sofa):
        raise TypeError((
            "Input must be a sofar.Sofa object "
            f"but is of type {str(type(sofa))}"))

    # Check for DataType
    if sofa.GLOBAL_DataType in ['FIR', 'FIR-E', 'FIRE']:
        # make a Signal
        signal = Signal(sofa.Data_IR, sofa.Data_SamplingRate)

    elif sofa.GLOBAL_DataType in ['TF', 'TF-E', 'TFE']:
        # make FrequencyData
        signal = FrequencyData(
            sofa.Data_Real + 1j * sofa.Data_Imag, sofa.N)
    else:
        raise ValueError(
            "DataType {sofa.GLOBAL_DataType} is not supported.")

    # Source
    s_values = sofa.SourcePosition
    s_domain, s_convention, s_unit = _sofa_pos(sofa.SourcePosition_Type)
    source_coordinates = Coordinates(
        s_values[:, 0],
        s_values[:, 1],
        s_values[:, 2],
        domain=s_domain,
        convention=s_convention,
        unit=s_unit)
    # Receiver
    r_values = sofa.ReceiverPosition
    r_domain, r_convention, r_unit = _sofa_pos(sofa.ReceiverPosition_Type)
    receiver_coordinates = Coordinates(
        r_values[:, 0],
        r_values[:, 1],
        r_values[:, 2],
        domain=r_domain,
        convention=r_convention,
        unit=r_unit)

    return signal, source_coordinates, receiver_coordinates


def _sofa_pos(pos_type):
    if pos_type == 'spherical':
        domain = 'sph'
        convention = 'top_elev'
        unit = 'deg'
    elif pos_type == 'cartesian':
        domain = 'cart'
        convention = 'right'
        unit = 'met'
    else:
        raise ValueError("Position:Type {pos_type} is not supported.")
    return domain, convention, unit


def read(filename):
    """
    Read any compatible pyfar object or numpy array (.far file) from disk.

    Parameters
    ----------
    filename : string, Path
        Input file. If no extension is provided, .far-suffix is added.

    Returns
    -------
    collection: dict
        Contains pyfar objects like
        ``{ 'name1': 'obj1', 'name2': 'obj2' ... }``.

    Examples
    --------
    Read signal and orientations objects stored in a .far file.

    >>> collection = pyfar.read('my_objs.far')
    >>> my_signal = collection['my_signal']
    >>> my_orientations = collection['my_orientations']
    """
    # Check for .far file extension
    filename = pathlib.Path(filename).with_suffix('.far')

    collection = {}
    with open(filename, 'rb') as f:
        zip_buffer = io.BytesIO()
        zip_buffer.write(f.read())
        with zipfile.ZipFile(zip_buffer) as zip_file:
            zip_paths = zip_file.namelist()
            obj_names_hints = [
                path.split('/')[:2] for path in zip_paths if '/$' in path]
            for name, hint in obj_names_hints:
                if codec._is_pyfar_type(hint[1:]):
                    obj = codec._decode_object_json_aided(name, hint, zip_file)
                elif hint == '$ndarray':
                    obj = codec._decode_ndarray(f'{name}/{hint}', zip_file)
                else:
                    raise TypeError(
                        '.far-file contains unknown types.'
                        'This might occur when writing and reading files with'
                        'different versions of Pyfar.')
                collection[name] = obj

        if 'builtin_wrapper' in collection:
            for key, value in collection['builtin_wrapper'].items():
                collection[key] = value
            collection.pop('builtin_wrapper')

    return collection


def write(filename, compress=False, **objs):
    """
    Write any compatible pyfar object or numpy array and often used builtin
    types as .far file to disk.

    Parameters
    ----------
    filename : string
        Full path or filename. If now extension is provided, .far-suffix
        will be add to filename.
    compress : bool
        Default is ``False`` (uncompressed).
        Compressed files take less disk space but need more time for writing
        and reading.
    **objs:
        Objects to be saved as key-value arguments, e.g.,
        ``name1=object1, name2=object2``.

    Examples
    --------

    Save Signal object, Orientations objects and numpy array to disk.

    >>> s = pyfar.Signal([1, 2, 3], 44100)
    >>> o = pyfar.Orientations.from_view_up([1, 0, 0], [0, 1, 0])
    >>> a = np.array([1,2,3])
    >>> pyfar.io.write('my_objs.far', signal=s, orientations=o, array=a)

    Notes
    -----
    * Supported builtin types are:
      bool, bytes, complex, float, frozenset, int, list, set, str and tuple
    """
    # Check for .far file extension
    filename = pathlib.Path(filename).with_suffix('.far')
    compression = zipfile.ZIP_STORED if compress else zipfile.ZIP_DEFLATED
    zip_buffer = io.BytesIO()
    builtin_wrapper = codec.BuiltinsWrapper()
    with zipfile.ZipFile(zip_buffer, "a", compression) as zip_file:
        for name, obj in objs.items():
            if codec._is_pyfar_type(obj):
                codec._encode_object_json_aided(obj, name, zip_file)
            elif codec._is_numpy_type(obj):
                codec._encode({f'${type(obj).__name__}': obj}, name, zip_file)
            elif type(obj) in codec._supported_builtin_types():
                builtin_wrapper[name] = obj
            else:
                error = (
                    f'Objects of type {type(obj)} cannot be written to disk.')
                if isinstance(obj, fo.Filter):
                    error = f'{error}. Consider casting to {fo.Filter}'
                raise TypeError(error)

        if len(builtin_wrapper) > 0:
            codec._encode_object_json_aided(
                builtin_wrapper, 'builtin_wrapper', zip_file)

    with open(filename, 'wb') as f:
        f.write(zip_buffer.getvalue())


def read_audio(filename, dtype='float64', **kwargs):
    """
    Import an audio file as :py:class:`~pyfar.classes.audio.Signal` object.

    Reads 'wav', 'aiff', 'ogg', and 'flac' files among others. For a complete
    list see :py:func:`audio_formats`.

    Parameters
    ----------
    filename : string, Path
        Input file.
    dtype : {'float64', 'float32', 'int32', 'int16'}, optional
        Data type of the returned signal, by default ``'float64'``.
        Floating point audio data is typically in the range from
        ``-1.0`` to ``1.0``.  Note that ``'int16'`` and ``'int32'`` should only
        be used if the data was written in the same format. Integer data is in
        the range from ``-2**15`` to ``2**15-1`` for ``'int16'`` and from
        ``-2**31`` to ``2**31-1`` for ``'int32'``.
    **kwargs
        Other keyword arguments to be passed to :py:func:`soundfile.read`. This
        is needed, e.g, to read RAW audio files.

    Returns
    -------
    signal : Signal
        :py:class:`~pyfar.classes.audio.Signal` object containing the audio
        data.

    Notes
    -----
    * This function is based on :py:func:`soundfile.read`.
    * Reading int values from a float file will *not* scale the data to
      [-1.0, 1.0). If the file contains ``np.array([42.6], dtype='float32')``,
      you will read ``np.array([43], dtype='int32')`` for ``dtype='int32'``.
    """
    data, sampling_rate = soundfile.read(
        file=filename, dtype=dtype, always_2d=True, **kwargs)
    signal = Signal(data.T, sampling_rate, domain='time', dtype=dtype)
    return signal


def write_audio(signal, filename, subtype=None, overwrite=True, **kwargs):
    """
    Write a :py:class:`~pyfar.classes.audio.Signal` object as a audio file to
    disk.

    Writes 'wav', 'aiff', 'ogg', and 'flac' files among others. For a complete
    list see :py:func:`audio_formats`.

    Parameters
    ----------
    signal : Signal
        Object to be written.
    filename : string, Path
        Output file. The format is determined from the file extension.
        See :py:func:`audio_formats` for all possible formats.
    subtype : str, optional
        The subtype of the sound file, the default value depends on the
        selected `format` (see :py:func:`default_audio_subtype`).
        See :py:func:`audio_subtypes` for all possible subtypes for
        a given ``format``.
    overwrite : bool
        Select wether to overwrite the audio file, if it already exists.
        The default is ``True``.
    **kwargs
        Other keyword arguments to be passed to :py:func:`soundfile.write`.

    Notes
    -----
    * Signals are flattened before writing to disk (e.g. a signal with
      ``cshape = (3, 2)`` will be written to disk as a six channel audio file).
    * This function is based on :py:func:`soundfile.write`.
    * Except for the subtypes ``'FLOAT'``, ``'DOUBLE'`` and ``'VORBIS'`` ´
      amplitudes larger than +/- 1 are clipped.

    """
    sampling_rate = signal.sampling_rate
    data = signal.time

    # Reshape to 2D
    data = data.reshape(-1, data.shape[-1])
    if len(signal.cshape) != 1:
        warnings.warn(f"Signal flattened to {data.shape[0]} channels.")

    # Check if file exists and for overwrite
    if overwrite is False and os.path.isfile(filename):
        raise FileExistsError(
            "File already exists,"
            "use overwrite option to disable error.")
    else:
        # Only the subtypes FLOAT, DOUBLE, VORBIS are not clipped,
        # see _clipped_audio_subtypes()
        format = pathlib.Path(filename).suffix[1:]
        if subtype is None:
            subtype = default_audio_subtype(format)
        if (np.any(data > 1.) and
                subtype.upper() not in ['FLOAT', 'DOUBLE', 'VORBIS']):
            warnings.warn(
                f'{format}-files of subtype {subtype} are clipped to +/- 1.')
        soundfile.write(
            file=filename, data=data.T, samplerate=sampling_rate,
            subtype=subtype, **kwargs)


def audio_formats():
    """Return a dictionary of available audio formats.

    Notes
    -----
    This function is a wrapper of :py:func:`soundfile.available_formats()`.

    Examples
    --------
    >>> import pyfar as pf
    >>> pf.io.audio_formats()
    {'FLAC': 'FLAC (FLAC Lossless Audio Codec)',
     'OGG': 'OGG (OGG Container format)',
     'WAV': 'WAV (Microsoft)',
     'AIFF': 'AIFF (Apple/SGI)',
     ...
     'WAVEX': 'WAVEX (Microsoft)',
     'RAW': 'RAW (header-less)',
     'MAT5': 'MAT5 (GNU Octave 2.1 / Matlab 5.0)'}

    """
    return soundfile.available_formats()


def audio_subtypes(format=None):
    """Return a dictionary of available audio subtypes.

    Parameters
    ----------
    format : str
        If given, only compatible subtypes are returned.

    Notes
    -----
    This function is a wrapper of :py:func:`soundfile.available_subtypes()`.

    Examples
    --------
    >>> import pyfar as pf
    >>> pf.io.audio_subtypes('FLAC')
    {'PCM_24': 'Signed 24 bit PCM',
     'PCM_16': 'Signed 16 bit PCM',
     'PCM_S8': 'Signed 8 bit PCM'}

    """
    return soundfile.available_subtypes(format=format)


def default_audio_subtype(format):
    """Return the default subtype for a given format.

    Notes
    -----
    This function is a wrapper of :py:func:`soundfile.default_audio_subtype()`.

    Examples
    --------
    >>> import pyfar as pf
    >>> pf.io.default_audio_subtype('WAV')
    'PCM_16'
    >>> pf.io.default_audio_subtype('MAT5')
    'DOUBLE'

    """
    return soundfile.default_subtype(format)


def read_comsol(filename, expressions=None):
    """Read exported data from COMSOL.

    Parameters
    ----------
    filename : str, Path
        Input file. Excepted input files are '.txt', '.dat' and '.csv'. '.csv'
        Files are strongly recommended, since .txt and .dat are inconvenient
        in their format.
    expressions : list[str], optional
        This list of expressions defines the output expressions. An example
        can be like ``expressions=['pabe.Lp_t']``. Also see
        :py:func:`~pyfar.dsp.comsol_read_header`. By default, all expressions
        get returned.

    Returns
    -------
    data : Signal or FrequencyData
        Returns a Signal or FrequencyData object depending on the input data.
    coordinates : Coordinates, optional
        A Coordinates Object based on the Input Data. If the input dimension is
        lower than three, the missing dimensions are set to zero. If there are
        no positions given, this parameter will not be returned.

    Raises
    ------
    SyntaxError
        Raises SyntaxError if the file format is not supported.
    ValueError
        Raises ValueError if the Frequency or Time data are inconvenient in the
        input file.

    Examples
    --------
    Returns all expressions
    >>> import pyfar as pf
    >>> data, coordinates = pf.io.read_comsol('my_comsol_data.csv')
    """

    # Check Datatype
    suffix = pathlib.Path(filename).suffix
    if not suffix.endswith(('.txt', '.dat', '.csv')):
        raise SyntaxError((
            "Input path must be a .txt, .csv or .dat file"
            f"but is of type {str(suffix)}"))

    # get header
    all_expressions, expressions_unit, parameters, domain, domain_data \
        = read_comsol_header(filename)
    header_data, is_complex, delimiter \
        = _read_comsol_header_get_headerline(filename)
    if 'dB' in expressions_unit:
        raise ResourceWarning("Do you really want to use dB-values?")

    # get meta data
    metadata = _read_comsol_metadata(filename)
    num_dimension = metadata['Dimension']
    num_notes = metadata['Nodes']
    num_entries = metadata['Expressions']
    num_expressions = len(all_expressions)

    # read body
    data_type = complex if is_complex else float
    domain_str = domain if domain == 'freq' else 't'
    read_data = np.loadtxt(
        filename,
        dtype=data_type,
        comments='%',
        converters=lambda s: s.replace('i', 'j'),
        encoding=None,
        delimiter=delimiter)

    # num_expressions.shape = (coordinates, Dimension+Expression)
    read_data = np.reshape(read_data, (num_notes, num_entries+num_dimension))

    # restructure data -> out a
    data_expressions = read_data[:, num_dimension:]
    order_domain = _remove_neighbored_duplicates(
        re.findall(domain_str + r'=([0-9.]+)', header_data))
    length_list = [len(order_domain)]
    dimension_list = [len(domain_data)]
    for para_name in parameters:
        a = _remove_neighbored_duplicates(
            re.findall(para_name + r'=([0-9.]+)', header_data))
        length_list.append(len(a))
        dimension_list.append(len(parameters[para_name]))
    indexes = np.argsort(length_list)
    new_shape = [num_notes]
    new_indexes = []
    for i in indexes:
        new_shape.append(dimension_list[i])
        new_indexes.append(i+1)
    new_shape.append(num_expressions)
    a = new_indexes.pop(-1)
    new_indexes.insert(0, a)
    new_indexes.append(0)
    data_expressions_shape = np.reshape(data_expressions, new_shape)

    # put into right dimensions
    switches = []
    sorting_indexes = list(new_indexes)
    for i in reversed(range(len(new_indexes))):
        if sorting_indexes[i] != i:
            idx = sorting_indexes.index(i)
            sorting_indexes[idx] = sorting_indexes[i]
            sorting_indexes[i] = i
            switches.append([i+1, idx+1])
    data_raw = data_expressions_shape
    for idxes in switches:
        data_raw = np.swapaxes(data_raw, idxes[0], idxes[1])

    # remove unwanted expressions
    if expressions is not None:
        indexes = [all_expressions.index(exp) for exp in expressions]
        indexes_remove = list(range(len(all_expressions)))
        [indexes_remove.remove(i) for i in sorted(indexes, reverse=True)]
        for i in sorted(indexes_remove, reverse=True):
            data_raw = np.delete(data_raw, i, 1)

    # create object
    comment = ', '.join(
        ' '.join(x) for x in zip(all_expressions, expressions_unit))
    if domain == 'freq':
        data = FrequencyData(
            data_raw, domain_data, dtype=data_type,
            comment=comment)
    else:
        data = TimeData(
            data_raw, domain_data, comment=comment)

    # read coordinates
    if num_dimension > 0:
        coords_data = read_data[:, 0:num_dimension].astype(np.float)
        x = coords_data[:, 0]
        y = coords_data[:, 1] if coords_data.shape[1] > 1 else np.zeros(
            coords_data[:, 0].shape)
        z = coords_data[:, 2] if coords_data.shape[1] > 2 else np.zeros(
            coords_data[:, 0].shape)
        coordinates = Coordinates(x, y, z)
        return data, coordinates
    return data, None


def read_comsol_header(filename):
    """Returns header information from exported data from COMSOL.

    Parameters
    ----------
    filename : str, Path
        Input file. Excepted input files are '.txt', '.dat' and '.csv'. '.csv'
        Files are strongly recommended, since .txt and .dat are inconvenient
        in their format.

    Returns
    -------
    expressions : list[str]
        This list of expressions defines the output expressions. An example
        can be like ``expressions=['pabe.p_t']``. Also see
        :py:func:`~pyfar.dsp.comsol_read`.
    expressions_unit : list[str]
        This list of expressions unit defines the units of the output
        expressions. An example can be like ``expressions_unit=['Pa']``.
    parameters : dict
        This dict contains all parameters ins from the input file. If no
        parameters are available, an emtpy dict is returnd. An example can be
        like ``parameters={'theta': [0.0, 0.7854], 'phi': [0., 1.5708]}``.
    domain : string
        Returns the domain of the input data. Note that ``'lambda'`` domain
        data is not allowed.

        ``'freq'``
            The data are in frequency domain.
        ``'time'``
            The data are in time domain.
    domain_data : list[]
        This list contains the domain data from the input file. Depending
        on the data in the input file, the output will be float or complex.

    Raises
    ------
    SyntaxError
        Raises SyntaxError if the file format is not supported.
    ValueError
        Raises ValueError if the domain is not supported.

    Examples
    --------
    Returns all expressions
    >>> import pyfar as pf
    >>> expressions, expressions_unit, parameters, domain, domain_data \
    >>>     = pf.io.read_comsol_header('my_comsol_data.csv')
    """
    # Check Datatype
    suffix = pathlib.Path(filename).suffix
    if not suffix.endswith(('.txt', '.dat', '.csv')):
        raise SyntaxError((
            "Input path must be a .txt, .csv or .dat file"
            f"but is of type {str(suffix)}"))

    # read header
    header_data, is_complex, delimiter \
        = _read_comsol_header_get_headerline(filename)

    # read expressions and expressions_units
    expressions_with_unit = re.findall(
        r'([a-zA-Z0-9\(\)\/\^ _.]+) @', header_data)

    expressions, idx = _real_comsol_header_find_unique(
        r'([a-zA-Z0-9\/\^_.]+) \(', ';'.join(expressions_with_unit))
    expressions_unit, idx = _real_comsol_header_find_unique(
        r'\(([a-zA-Z0-9\/\^ .]+)\)', ';'.join(expressions_with_unit), idx)

    # read parameter
    parameter_names, idx = _real_comsol_header_find_unique(
        r'([a-zA-Z0-9\/\^_.]+)=', header_data)
    parameters = dict()
    domain_str = ''
    for para_name in parameter_names:
        unit, idx = _real_comsol_header_find_unique(
            para_name + r'=[0-9.]+([a-zA-Z]+)', header_data)
        values, idx = _real_comsol_header_find_unique(
            para_name + r'=([0-9.]+)', header_data)
        values = [float(x) for x in values]
        if para_name in ['t', 'freq']:
            domain_data = values
            domain_str = para_name
            continue
        if len(unit) == 0:
            parameters[para_name] = values
        else:
            parameters[para_name] = [x+unit for x in values]

    # read domain data
    if domain_str == 't':
        domain = 'time'
    elif domain_str == 'freq':
        domain = domain_str
    else:
        domain_str = np.unique(re.findall(
            r'@ ([a-zA-Z]+)=', header_data))[0]
        raise ValueError(domain_str + " as domain data is not allowed.")
    return expressions, expressions_unit, parameters, domain, domain_data


def _remove_neighbored_duplicates(a):
    res = [a[0]]
    for i, c in enumerate(a[1:]):
        if c != a[i]:
            res.append(c)
    return res


def _read_comsol_metadata(filename):
    suffix = pathlib.Path(filename).suffix
    metadata = dict()
    seperator_header = ','
    with open(filename) as f:
        last_line = f.readline()
        while True:
            line = f.readline()
            if line[0] != '%':
                break
            elif len(last_line) > 0:
                number_names = ['dimension', 'nodes', 'expressions']
                if suffix.endswith('.csv'):
                    last_line = last_line[2:-1].replace('"', '').split(
                        seperator_header)
                elif suffix.endswith('.dat') or suffix.endswith('.txt'):
                    last_line = " ".join(last_line[2:-1].replace(',', ';')
                                         .replace(':', ',').split()
                                         ).split(seperator_header)
                if any(number_name == last_line[0].lower() for number_name in
                       number_names):
                    metadata[last_line[0]] = int(last_line[-1])
                else:
                    if suffix.endswith('.csv'):
                        metadata[last_line[0]] = ",".join(last_line[1:])
                    elif suffix.endswith('.dat') or suffix.endswith('.txt'):
                        last_line[1] = last_line[1][1:]
                        metadata[last_line[0]] = ":".join(
                            last_line[1:]).replace(';', ',')
                last_line = line

    return metadata


def _real_comsol_header_find_unique(pattern, string, idx=None):
    if idx is None:
        expressions, idx = np.unique(re.findall(
            pattern,
            string), True)
        idx.sort()
    expressions_all = re.findall(
        pattern,
        string)
    expressions = []
    [expressions.append(expressions_all[i]) for i in idx]
    return expressions, idx


def _read_comsol_header_get_headerline(filename):
    header_data = []
    with open(filename) as f:
        last_line = []
        for idx, line in enumerate(f):
            if line[0] != '%':
                header_data = last_line
                break
            last_line = line
    delimiter = ',' if ',' in line else None
    return header_data[2:].replace('\n', ''), 'i' in line, delimiter


def _clipped_audio_subtypes():
    """Creates a dictionary of format/subtype combinations which are clipped by
    :py:func:´write_audio`.

    This function is not called directly due to the need of writing all files
    to disk. It needs to be called manually:
    pyfar.io.io._clipped_audio_subtypes().
    """
    collection = {}
    signal = pyfar.Signal([-1.5, -1, -.5, 0, .5, 1, 1.5] * 100, 44100)
    with tempfile.TemporaryDirectory() as tmpdir:
        formats = pyfar.io.audio_formats()
        for format in formats:
            filename = os.path.join(tmpdir, 'test_file.' + format)
            for subtype in pyfar.io.audio_subtypes(format):
                write_valid = not _soundfile_write_errors(format, subtype)
                read_valid = not _soundfile_read_errors(format, subtype)
                format_valid = soundfile.check_format(format, subtype)
                if write_valid and read_valid and format_valid:
                    if format == 'RAW':
                        write_audio(signal, filename, subtype=subtype)
                        signal_read = read_audio(
                            filename, samplerate=44100, channels=1,
                            subtype=subtype)
                    else:
                        write_audio(signal, filename, subtype=subtype)
                        signal_read = read_audio(filename)
                    if (np.any(signal_read.time > 1.1) and
                            np.any(signal_read.time < -1.1)):
                        behavior = 'not clipping (' + format + ')'
                    elif (np.any(signal_read.time > .1) and
                          np.any(signal_read.time < -.1)):
                        behavior = 'clipping to +/- 1 (' + format + ')'
                    else:
                        raise ValueError(f"{format}/{subtype}")

                    if subtype not in collection:
                        collection[subtype] = [behavior]
                    else:
                        collection[subtype] = collection[subtype] + [behavior]

    return collection


def _soundfile_write_errors(format, subtype):
    """Checks if a write error due to soundfile/libsnfile can be expected.

    Written according to test_write_audio_read_audio.
    """
    if format == 'AIFF' and subtype == 'DWVW_12':
        error_expected = True
    else:
        error_expected = False
    return error_expected


def _soundfile_read_errors(format, subtype):
    """Checks if a read error due to soundfile/libsnfile can be expected.

    Written according to test_write_audio_read_audio.
    """
    if 'DWVW' in subtype and (format == 'AIFF' or format == 'RAW'):
        error_expected = True
    else:
        error_expected = False
    return error_expected
