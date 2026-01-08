"""Unit tests for geometry module."""

import pytest
import math
from mrtools.geometry import (
    transform_vertex,
    calculate_polygon_area_3d,
    calculate_surface_area,
)


class TestTransformVertex:
    """Tests for vertex coordinate transformation."""

    def test_identity_transform(self):
        """Test with identity transform (no scaling or translation)."""
        vertex = [100, 200, 300]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}
        result = transform_vertex(vertex, transform)
        assert result == (100.0, 200.0, 300.0)

    def test_scale_only(self):
        """Test with only scaling applied."""
        vertex = [100, 200, 300]
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}
        result = transform_vertex(vertex, transform)
        assert result == (0.1, 0.2, 0.3)

    def test_translate_only(self):
        """Test with only translation applied."""
        vertex = [100, 200, 300]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [1000.0, 2000.0, 3000.0]}
        result = transform_vertex(vertex, transform)
        assert result == (1100.0, 2200.0, 3300.0)

    def test_scale_and_translate(self):
        """Test with both scaling and translation (typical CityJSON case)."""
        vertex = [100, 200, 300]
        transform = {
            "scale": [0.001, 0.001, 0.001],
            "translate": [85000.0, 446000.0, 50.0],
        }
        result = transform_vertex(vertex, transform)
        assert result == (85000.1, 446000.2, 50.3)


class TestCalculatePolygonArea3D:
    """Tests for 3D polygon area calculation using Newell's method."""

    def test_horizontal_square(self):
        """Test area of a horizontal square (1x1) in XY plane at z=0."""
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 1.0) < 1e-10

    def test_horizontal_rectangle(self):
        """Test area of a horizontal rectangle (2x3) in XY plane."""
        vertices = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 3.0, 0.0), (0.0, 3.0, 0.0)]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 6.0) < 1e-10

    def test_vertical_square_xz(self):
        """Test area of a vertical square (1x1) in XZ plane."""
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.0, 1.0)]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 1.0) < 1e-10

    def test_vertical_square_yz(self):
        """Test area of a vertical square (1x1) in YZ plane."""
        vertices = [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 1.0), (0.0, 0.0, 1.0)]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 1.0) < 1e-10

    def test_triangle(self):
        """Test area of a right triangle (base=3, height=4, area=6)."""
        vertices = [(0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (0.0, 4.0, 0.0)]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 6.0) < 1e-10

    def test_sloped_square(self):
        """Test area of a square tilted in 3D space."""
        # Square with corners at (0,0,0), (1,0,0), (1,1,1), (0,1,1)
        # This is a square with side length sqrt(2) tilted in space
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 1.0, 1.0), (0.0, 1.0, 1.0)]
        area = calculate_polygon_area_3d(vertices)
        expected_area = math.sqrt(2)  # Side length is sqrt(1^2 + 1^2) = sqrt(2)
        assert abs(area - expected_area) < 1e-10

    def test_degenerate_no_vertices(self):
        """Test with no vertices returns zero area."""
        vertices = []
        area = calculate_polygon_area_3d(vertices)
        assert area == 0.0

    def test_degenerate_one_vertex(self):
        """Test with one vertex returns zero area."""
        vertices = [(0.0, 0.0, 0.0)]
        area = calculate_polygon_area_3d(vertices)
        assert area == 0.0

    def test_degenerate_two_vertices(self):
        """Test with two vertices returns zero area."""
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0)]
        area = calculate_polygon_area_3d(vertices)
        assert area == 0.0

    def test_large_scale(self):
        """Test with large coordinates (typical for real-world coordinates)."""
        vertices = [
            (85000.0, 446000.0, 0.0),
            (85010.0, 446000.0, 0.0),
            (85010.0, 446010.0, 0.0),
            (85000.0, 446010.0, 0.0),
        ]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 100.0) < 1e-8  # 10x10 = 100

    def test_cube_face(self):
        """Test area of one face of a unit cube."""
        # Front face of unit cube
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 1.0), (0.0, 0.0, 1.0)]
        area = calculate_polygon_area_3d(vertices)
        assert abs(area - 1.0) < 1e-10

    def test_pentagon(self):
        """Test area of a regular pentagon."""
        # Regular pentagon with radius 1 centered at origin
        n = 5
        radius = 1.0
        vertices = []
        for i in range(n):
            angle = 2 * math.pi * i / n
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            vertices.append((x, y, 0.0))

        area = calculate_polygon_area_3d(vertices)
        # Area of regular pentagon = (5/4) * s^2 * cot(π/5)
        # For unit radius: approximately 2.377
        expected_area = (5 / 4) * (2 * radius * math.sin(math.pi / 5)) ** 2 / math.tan(
            math.pi / 5
        )
        assert abs(area - expected_area) < 1e-10


class TestCalculateSurfaceArea:
    """Tests for surface area calculation with boundary rings."""

    def test_simple_square_boundary(self):
        """Test surface with a simple square boundary."""
        # Vertex indices for a 1x1 square
        vertices_global = [
            [0, 0, 0],
            [1000, 0, 0],  # 1.0 after scale
            [1000, 1000, 0],  # 1.0, 1.0 after scale
            [0, 1000, 0],  # 0.0, 1.0 after scale
        ]
        boundary = [[0, 1, 2, 3]]  # Outer ring only
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}

        area = calculate_surface_area(boundary, vertices_global, transform)
        assert abs(area - 1.0) < 1e-10

    def test_rectangle_with_transform(self):
        """Test rectangle with realistic CityJSON transform."""
        vertices_global = [
            [0, 0, 0],
            [10000, 0, 0],  # 10.0m after scale
            [10000, 5000, 0],  # 10.0m, 5.0m
            [0, 5000, 0],  # 0.0m, 5.0m
        ]
        boundary = [[0, 1, 2, 3]]
        transform = {
            "scale": [0.001, 0.001, 0.001],
            "translate": [85000.0, 446000.0, 50.0],
        }

        area = calculate_surface_area(boundary, vertices_global, transform)
        assert abs(area - 50.0) < 1e-8  # 10 * 5 = 50

    def test_boundary_with_hole(self):
        """Test that holes (inner rings) are correctly subtracted from outer ring."""
        # Outer square (2x2)
        vertices_global = [
            [0, 0, 0],
            [2000, 0, 0],
            [2000, 2000, 0],
            [0, 2000, 0],
            # Inner square (1x1) - hole that should be subtracted
            [500, 500, 0],
            [1500, 500, 0],
            [1500, 1500, 0],
            [500, 1500, 0],
        ]
        boundary = [[0, 1, 2, 3], [4, 5, 6, 7]]  # Outer ring + hole
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}

        area = calculate_surface_area(boundary, vertices_global, transform)
        # Should return outer ring area minus hole: 4.0 - 1.0 = 3.0
        assert abs(area - 3.0) < 1e-10

    def test_empty_boundary(self):
        """Test with empty boundary returns zero."""
        vertices_global = [[0, 0, 0]]
        boundary = []
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        area = calculate_surface_area(boundary, vertices_global, transform)
        assert area == 0.0

    def test_degenerate_boundary_too_few_vertices(self):
        """Test boundary with less than 3 vertices returns zero."""
        vertices_global = [[0, 0, 0], [1000, 0, 0]]
        boundary = [[0, 1]]  # Only 2 vertices
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}

        area = calculate_surface_area(boundary, vertices_global, transform)
        assert area == 0.0

    def test_triangle_boundary(self):
        """Test triangular surface area."""
        # Right triangle with base=3, height=4, area=6
        vertices_global = [[0, 0, 0], [3000, 0, 0], [0, 4000, 0]]
        boundary = [[0, 1, 2]]
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}

        area = calculate_surface_area(boundary, vertices_global, transform)
        assert abs(area - 6.0) < 1e-10
