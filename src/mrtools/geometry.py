"""Geometric calculations for CityJSON processing."""

import math
from typing import List, Tuple, Dict, Any


def transform_vertex(
    vertex: List[int], transform: Dict[str, List[float]]
) -> Tuple[float, float, float]:
    """
    Transform compressed vertex coordinates to real-world coordinates.

    CityJSON uses a compression scheme where vertices are stored as integers
    and need to be scaled and translated to get real coordinates.

    Args:
        vertex: List of 3 integers [x, y, z] representing compressed coordinates
        transform: Dictionary with 'scale' and 'translate' arrays

    Returns:
        Tuple of (x, y, z) real-world coordinates
    """
    scale = transform["scale"]
    translate = transform["translate"]

    x = vertex[0] * scale[0] + translate[0]
    y = vertex[1] * scale[1] + translate[1]
    z = vertex[2] * scale[2] + translate[2]

    return (x, y, z)


def calculate_polygon_area_3d(vertices: List[Tuple[float, float, float]]) -> float:
    """
    Calculate the area of a 3D polygon using Newell's method.

    Newell's method computes the normal vector of a polygon and uses its
    magnitude to determine the area. This method:
    - Works for non-planar polygons (projects to best-fit plane)
    - Handles any orientation in 3D space
    - Is numerically stable

    The formula computes the components of the normal vector N = (nx, ny, nz):
    - nx = Σ(yi - yi+1)(zi + zi+1)
    - ny = Σ(zi - zi+1)(xi + xi+1)
    - nz = Σ(xi - xi+1)(yi + yi+1)

    Area = |N| / 2 = sqrt(nx² + ny² + nz²) / 2

    Args:
        vertices: List of 3D coordinates [(x, y, z), ...]

    Returns:
        Area of the polygon in square units
    """
    n = len(vertices)
    if n < 3:
        return 0.0

    # Calculate normal vector components using Newell's method
    nx, ny, nz = 0.0, 0.0, 0.0

    for i in range(n):
        v1 = vertices[i]
        v2 = vertices[(i + 1) % n]  # Next vertex (wraps around)

        nx += (v1[1] - v2[1]) * (v1[2] + v2[2])
        ny += (v1[2] - v2[2]) * (v1[0] + v2[0])
        nz += (v1[0] - v2[0]) * (v1[1] + v2[1])

    # Area is half the magnitude of the normal vector
    area = 0.5 * math.sqrt(nx * nx + ny * ny + nz * nz)
    return area


def calculate_surface_area(
    boundary: List[List[int]],
    vertices_global: List[List[int]],
    transform: Dict[str, List[float]],
) -> float:
    """
    Calculate the area of a surface from its boundary representation.

    A boundary in CityJSON can have multiple rings:
    - First ring (index 0): outer boundary
    - Subsequent rings: holes (inner rings)

    The total area is calculated as the outer ring area minus the area of all holes.

    Args:
        boundary: List of rings, where each ring is a list of vertex indices
        vertices_global: Global vertices array from CityJSON root
        transform: Transform object with scale and translate

    Returns:
        Area of the surface in square units
    """
    if not boundary or len(boundary) == 0:
        return 0.0

    # Calculate outer ring area (first ring)
    outer_ring_indices = boundary[0]

    if len(outer_ring_indices) < 3:
        return 0.0

    # Transform vertices to real-world coordinates
    coords_3d = [
        transform_vertex(vertices_global[idx], transform) for idx in outer_ring_indices
    ]

    # Calculate area using Newell's method
    outer_area = calculate_polygon_area_3d(coords_3d)

    # Subtract area of holes (inner rings)
    for inner_ring_indices in boundary[1:]:
        if len(inner_ring_indices) >= 3:
            inner_coords_3d = [
                transform_vertex(vertices_global[idx], transform)
                for idx in inner_ring_indices
            ]
            hole_area = calculate_polygon_area_3d(inner_coords_3d)
            outer_area -= hole_area

    return outer_area
