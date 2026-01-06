"""Unit tests for processor module."""

import pytest
from mrtools.processor import (
    get_surface_semantic_type,
    extract_roof_surfaces,
    calculate_roof_area_for_object,
)


class TestGetSurfaceSemanticType:
    """Tests for semantic type extraction."""

    def test_solid_roof_surface(self):
        """Test getting RoofSurface type from Solid geometry."""
        semantics = {
            "surfaces": [
                {"type": "GroundSurface"},
                {"type": "RoofSurface"},
                {"type": "WallSurface"},
            ],
            "values": [[0, 1, 2, 2, 1]],  # shell 0 has 5 faces
        }
        result = get_surface_semantic_type((0, 1), semantics, "Solid")
        assert result == "RoofSurface"

    def test_multisurface_roof_surface(self):
        """Test getting RoofSurface type from MultiSurface geometry."""
        semantics = {
            "surfaces": [
                {"type": "GroundSurface"},
                {"type": "WallSurface"},
                {"type": "RoofSurface"},
            ],
            "values": [0, 1, 1, 2, 2],  # 5 faces
        }
        result = get_surface_semantic_type(3, semantics, "MultiSurface")
        assert result == "RoofSurface"

    def test_no_semantics(self):
        """Test with missing semantics returns None."""
        result = get_surface_semantic_type(0, None, "MultiSurface")
        assert result is None

    def test_missing_values(self):
        """Test with missing values key returns None."""
        semantics = {
            "surfaces": [{"type": "RoofSurface"}],
        }
        result = get_surface_semantic_type(0, semantics, "MultiSurface")
        assert result is None

    def test_index_out_of_bounds(self):
        """Test with out of bounds index returns None."""
        semantics = {
            "surfaces": [{"type": "RoofSurface"}],
            "values": [0, 0],
        }
        result = get_surface_semantic_type(5, semantics, "MultiSurface")
        assert result is None


class TestExtractRoofSurfaces:
    """Tests for roof surface extraction."""

    def test_multisurface_with_roofs(self):
        """Test extracting roof surfaces from MultiSurface geometry."""
        geometry = {
            "type": "MultiSurface",
            "boundaries": [
                [[0, 1, 2, 3]],  # Ground
                [[4, 5, 6, 7]],  # Wall
                [[8, 9, 10, 11]],  # Roof 1
                [[12, 13, 14, 15]],  # Roof 2
            ],
            "semantics": {
                "surfaces": [
                    {"type": "GroundSurface"},
                    {"type": "WallSurface"},
                    {"type": "RoofSurface"},
                ],
                "values": [0, 1, 2, 2],
            },
        }
        # Simple vertices for a 1x1 square
        vertices_global = [[i, 0, 0] for i in range(16)]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        roof_areas = extract_roof_surfaces(geometry, vertices_global, transform)
        assert len(roof_areas) == 2  # Two roof surfaces

    def test_solid_with_roofs(self):
        """Test extracting roof surfaces from Solid geometry."""
        geometry = {
            "type": "Solid",
            "boundaries": [
                [  # Shell 0
                    [[0, 1, 2, 3]],  # Ground (semantic 0)
                    [[4, 5, 6, 7]],  # Roof (semantic 1)
                    [[8, 9, 10, 11]],  # Wall (semantic 2)
                ]
            ],
            "semantics": {
                "surfaces": [
                    {"type": "GroundSurface"},
                    {"type": "RoofSurface"},
                    {"type": "WallSurface"},
                ],
                "values": [[0, 1, 2]],
            },
        }
        vertices_global = [[i, 0, 0] for i in range(12)]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        roof_areas = extract_roof_surfaces(geometry, vertices_global, transform)
        assert len(roof_areas) == 1  # One roof surface

    def test_no_semantics(self):
        """Test with no semantics returns empty list."""
        geometry = {
            "type": "MultiSurface",
            "boundaries": [[[0, 1, 2, 3]]],
        }
        vertices_global = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        roof_areas = extract_roof_surfaces(geometry, vertices_global, transform)
        assert len(roof_areas) == 0

    def test_no_roof_surfaces(self):
        """Test with only walls and ground returns empty list."""
        geometry = {
            "type": "MultiSurface",
            "boundaries": [[[0, 1, 2, 3]], [[4, 5, 6, 7]]],
            "semantics": {
                "surfaces": [
                    {"type": "GroundSurface"},
                    {"type": "WallSurface"},
                ],
                "values": [0, 1],
            },
        }
        vertices_global = [[i, 0, 0] for i in range(8)]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        roof_areas = extract_roof_surfaces(geometry, vertices_global, transform)
        assert len(roof_areas) == 0


class TestCalculateRoofAreaForObject:
    """Tests for CityObject roof area calculation."""

    def test_object_with_single_geometry(self):
        """Test object with one geometry containing roof surfaces."""
        obj_data = {
            "type": "Building",
            "geometry": [
                {
                    "type": "MultiSurface",
                    "boundaries": [
                        [[0, 1, 2, 3]],  # Roof - 10x10 square
                    ],
                    "semantics": {
                        "surfaces": [{"type": "RoofSurface"}],
                        "values": [0],
                    },
                }
            ],
        }
        vertices_global = [
            [0, 0, 0],
            [10000, 0, 0],
            [10000, 10000, 0],
            [0, 10000, 0],
        ]
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}

        total_area = calculate_roof_area_for_object(obj_data, vertices_global, transform)
        assert abs(total_area - 100.0) < 1e-8  # 10 * 10 = 100

    def test_object_with_multiple_geometries(self):
        """Test object with multiple geometries."""
        obj_data = {
            "type": "Building",
            "geometry": [
                {
                    "type": "MultiSurface",
                    "boundaries": [[[0, 1, 2, 3]]],  # 5x5 = 25
                    "semantics": {
                        "surfaces": [{"type": "RoofSurface"}],
                        "values": [0],
                    },
                },
                {
                    "type": "MultiSurface",
                    "boundaries": [[[0, 1, 2, 3]]],  # 3x3 = 9
                    "semantics": {
                        "surfaces": [{"type": "RoofSurface"}],
                        "values": [0],
                    },
                },
            ],
        }
        vertices_global = [
            [0, 0, 0],
            [5000, 0, 0],  # First roof: 5x5
            [5000, 5000, 0],
            [0, 5000, 0],
        ]
        transform = {"scale": [0.001, 0.001, 0.001], "translate": [0.0, 0.0, 0.0]}

        # Both geometries use same vertices, so 25 + 25 = 50
        total_area = calculate_roof_area_for_object(obj_data, vertices_global, transform)
        assert abs(total_area - 50.0) < 1e-8

    def test_object_with_no_geometry(self):
        """Test object with no geometry returns 0."""
        obj_data = {
            "type": "Building",
            "geometry": [],
        }
        vertices_global = [[0, 0, 0]]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        total_area = calculate_roof_area_for_object(obj_data, vertices_global, transform)
        assert total_area == 0.0

    def test_object_with_no_semantics(self):
        """Test object with geometry but no semantics returns 0."""
        obj_data = {
            "type": "Building",
            "geometry": [
                {
                    "type": "MultiSurface",
                    "boundaries": [[[0, 1, 2, 3]]],
                }
            ],
        }
        vertices_global = [[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0]]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        total_area = calculate_roof_area_for_object(obj_data, vertices_global, transform)
        assert total_area == 0.0

    def test_object_with_only_walls(self):
        """Test object with only wall surfaces returns 0."""
        obj_data = {
            "type": "Building",
            "geometry": [
                {
                    "type": "MultiSurface",
                    "boundaries": [[[0, 1, 2, 3]]],
                    "semantics": {
                        "surfaces": [{"type": "WallSurface"}],
                        "values": [0],
                    },
                }
            ],
        }
        vertices_global = [[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0]]
        transform = {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]}

        total_area = calculate_roof_area_for_object(obj_data, vertices_global, transform)
        assert total_area == 0.0
