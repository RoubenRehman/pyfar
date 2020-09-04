from pytest import raises, fixture

import numpy as np
from scipy.spatial.transform import Rotation

from haiopy.orientations import Orientations
from haiopy.coordinates import Coordinates


def test_orientations_init():
    """Init `Orientations` without optional parameters."""
    orient = Orientations()
    assert isinstance(orient, Orientations)


def test_orientations_from_view_up():
    """Create `Orientations` from view and up vectors."""
    # test with single view and up vectors
    view = [1, 0, 0]
    up = [0, 1, 0]
    Orientations.from_view_up(view, up)
    # test with multiple view and up vectors
    views = [[1, 0, 0], [0, 0, 1]]
    ups = [[0, 1, 0], [0, 1, 0]]
    Orientations.from_view_up(views, ups)
    # provided as ndarrays
    views = np.atleast_2d(views).astype(np.float64)
    ups = np.atleast_2d(ups).astype(np.float64)
    Orientations.from_view_up(views, ups)
    # provided as Coordinates
    views = Coordinates(views[:, 0], views[:, 1], views[:, 2])
    ups = Coordinates(ups[:, 0], ups[:, 1], ups[:, 2])
    Orientations.from_view_up(views, ups)
    # view and up counts not matching
    views = [[1, 0, 0], [0, 0, 1]]
    ups = [[0, 1, 0]]
    Orientations.from_view_up(views, ups)


def test_orientations_from_view_up_invalid():
    """Try to create `Orientations` from invalid view and up vectors."""
    # mal-formed lists
    views = [[1, 0, 0], [0, 0]]
    ups = [[0, 1, 0], [0, 0, 0]]
    with raises(ValueError):
        Orientations.from_view_up(views, ups)
    # any of views and ups has zero-length
    views = [[1, 0, 0], [0, 0, 1]]
    ups = [[0, 1, 0], [0, 0, 0]]
    with raises(ValueError):
        Orientations.from_view_up(views, ups)
    # views' and ups' shape must be (N, 3) or (3,)
    views = [0, 1]
    ups = [0, 1]
    with raises(ValueError):
        Orientations.from_view_up(views, ups)
    # view and up vectors must be orthogonal
    views = [1.0, 0.5, 0.1]
    ups = [0, 0, 1]
    with raises(ValueError):
        Orientations.from_view_up(views, ups)


@fixture
def views():
    return [[1, 0, 0], [2, 0, 0]]


@fixture
def ups():
    return [[0, 1, 0], [0, -2, 0]]


@fixture
def positions():
    return [[0, 0.5, 0], [0, -0.5, 0]]


@fixture
def orientations(views, ups):
    return Orientations.from_view_up(views, ups)


def test_orientations_show(views, ups, positions, orientations):
    """
    Visualize orientations via `Orientations.show()`
    with and without `positions`.
    """
    # default orientation
    Orientations().show()
    # single vectors no position
    view = [1, 0, 0]
    up = [0, 1, 0]
    orientation_single = Orientations.from_view_up(view, up)
    orientation_single.show()
    # with position
    position = Coordinates(0, 1, 0)
    orientation_single.show(position)

    # multiple vectors no position
    orientations.show()
    # with matching number of positions
    orientations.show(positions)

    # select what to show
    orientations.show(show_views=False)
    orientations.show(show_ups=False)
    orientations.show(show_rights=False)
    orientations.show(show_views=False, show_ups=False)
    orientations.show(show_views=False, show_rights=False)
    orientations.show(show_ups=False, show_rights=False)
    orientations.show(positions=positions, show_views=False, show_ups=False)
    
    # with positions provided as Coordinates
    positions = Coordinates([0, 5], [0, 0], [0, 0])
    orientations.show(positions)
    # with non-matching positions
    positions = Coordinates(0, 1, 0)
    with raises(ValueError):
        orientations.show(positions)


def test_orientations_from_view_up_show_coordinate_system_change(views, ups):
    """
    Create `Orientations` from view and up vectors in the spherical domain
    as well as in the carteesian domain, and visualize both to compare them
    manually by eye.
    """
    # Carteesian: Visualize to manually validate orientations
    views = np.asarray(views)
    ups = np.asarray(ups)
    views = Coordinates(views[:, 0], views[:, 1], views[:, 2])
    ups = Coordinates(ups[:, 0], ups[:, 1], ups[:, 2])

    positions = Coordinates([0, 0], [0.5, -0.5], [0, 0])
    orient_from_cart = Orientations.from_view_up(views, ups)
    orient_from_cart.show(positions)

    # Convert to spherical: And again visualize to manually validate
    views.get_sph()
    ups.get_sph()
    positions.get_sph()

    orient_from_sph = Orientations.from_view_up(views, ups)
    orient_from_sph.show(positions)

    # Check if coordinate system has not been changed by orientations
    assert views._system['domain'] == 'sph', (
        "Coordinate system has been changed by Orientations.")
    assert ups._system['domain'] == 'sph', (
        "Coordinate system has been changed by Orientations.")
    assert positions._system['domain'] == 'sph', (
        "Coordinate system has been changed by Orientations.show().")


def test_as_view_up_right(views, ups, orientations):
    """"""
    views_, ups_, rights_ = orientations.as_view_up_right()


def test_orientations_indexing(orientations):
    """
    Apply index-operator `[]` on `Orientations` to get a single quaternion.
    """
    orientations[0]
    orientations[1]
    with raises(IndexError):
        orientations[2]

    quats = orientations.as_quat()
    assert np.array_equal(quats[0], orientations[0].as_quat()), (
        "Indexed orientations are not the same")
    assert np.array_equal(quats[1], orientations[1].as_quat()), (
        "Indexed orientations are not the same")


def test_orientations_indexing_assignment(orientations):
    """
    Assign a new value to a quaternion of an `Orientation`
    via the index-operator `[]`.
    """
    orientations[0] = Orientations([0, 0, 0, 1])
    orientations[0] = Orientations.from_view_up([0, 0, 1], [1, 0, 0])
    orientations[0] = [0, 0, 0, 1]
    orientations[:] = [[0, 0, 0, 1], [0, 0, 1, 0]]
    with raises(ValueError):
        orientations[0] = [0, 0, 3]
    with raises(ValueError):
        orientations[0] = orientations


def test_orientations_rotation(views, ups, positions, orientations):
    """Multiply an Orientation with a Rotation and visualize them."""
    orientations.show(positions)
    # Rotate first Orientation around z-axis by 45°
    rot_z45 = Rotation.from_euler('z', 45, degrees=True)
    orientations[0] = orientations[0] * rot_z45
    orientations.show(positions)
    # Rotate second Orientation around x-axis by 45°
    rot_x45 = Rotation.from_euler('x', 45, degrees=True)
    orientations[1] = orientations[1] * rot_x45
    orientations.show(positions)
    # Rotate both Orientations at once
    orientations = Orientations.from_view_up(views, ups)
    orientations = orientations * rot_x45
    orientations.show(positions)
