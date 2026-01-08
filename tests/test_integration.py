"""Integration tests using test fixtures."""

import json
import tempfile
from pathlib import Path

import pytest

from mrtools.processor import process_cityjson


class TestCityJSONIntegration:
    """Integration tests with complete CityJSON files."""

    def test_cube_fixture(self):
        """Test processing cube with known roof area (10x10 = 100)."""
        fixture_path = Path(__file__).parent / "fixtures" / "cube.city.json"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_cityjson(fixture_path, output_path)

            # Check that attribute was added
            cube_obj = result["CityObjects"]["cube-1"]
            assert "total_area_roof" in cube_obj["attributes"]

            # Cube has one roof surface (top face) with area 10x10 = 100
            roof_area = cube_obj["attributes"]["total_area_roof"]
            assert abs(roof_area - 100.0) < 1e-8

            # Verify output file was written
            assert output_path.exists()

            # Verify output is valid JSON
            with open(output_path) as f:
                output_data = json.load(f)
            assert output_data["type"] == "CityJSON"

        finally:
            output_path.unlink()

    def test_torus_fixture(self):
        """Test processing torus to see if holes in surfaces is supported."""
        fixture_path = Path(__file__).parent / "fixtures" / "torus.city.json"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_cityjson(fixture_path, output_path)

            # Check that attribute was added
            torus_obj = result["CityObjects"]["id-1"]
            assert "total_area_roof" in torus_obj["attributes"]

            # Torus has one roof surface (top face) with area 1x1-smth
            roof_area = torus_obj["attributes"]["total_area_roof"]
            assert abs(roof_area - 0.875) < 1e-8

            # Verify output file was written
            assert output_path.exists()

            # Verify output is valid JSON
            with open(output_path) as f:
                output_data = json.load(f)
            assert output_data["type"] == "CityJSON"

        finally:
            output_path.unlink()

    def test_simple_house_fixture(self):
        """Test processing house with pyramid roof."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple_house.city.json"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_cityjson(fixture_path, output_path)

            house_obj = result["CityObjects"]["house-1"]
            assert "total_area_roof" in house_obj["attributes"]

            # House has 4 triangular roof surfaces forming a pyramid
            # Base is 5x5 meters, apex at height 5m
            # Each triangle has base 5m and slant height sqrt(2.5^2 + 2^2) = sqrt(10.25)
            # Area of each triangle = 0.5 * 5 * sqrt(10.25)
            # Total roof area = 4 * 0.5 * 5 * sqrt(10.25) = 10 * sqrt(10.25) ≈ 32.02
            roof_area = house_obj["attributes"]["total_area_roof"]
            assert roof_area > 0.0
            # Just verify it's a reasonable value (between 30 and 35)
            assert 30.0 < roof_area < 35.0

        finally:
            output_path.unlink()

    def test_no_semantics_fixture(self):
        """Test processing building with no semantic information."""
        fixture_path = Path(__file__).parent / "fixtures" / "no_semantics.city.json"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_cityjson(fixture_path, output_path)

            building_obj = result["CityObjects"]["building-no-semantics"]
            assert "total_area_roof" in building_obj["attributes"]

            # No semantics means no roof surfaces identified
            roof_area = building_obj["attributes"]["total_area_roof"]
            assert roof_area == 0.0

        finally:
            output_path.unlink()

    def test_preserves_other_attributes(self):
        """Test that processing preserves existing attributes."""
        # Create fixture with existing attributes
        cityjson_data = {
            "type": "CityJSON",
            "version": "2.0",
            "transform": {
                "scale": [1.0, 1.0, 1.0],
                "translate": [0.0, 0.0, 0.0],
            },
            "CityObjects": {
                "test-building": {
                    "type": "Building",
                    "attributes": {"existing_attr": "preserved", "year_built": 2020},
                    "geometry": [
                        {
                            "type": "MultiSurface",
                            "boundaries": [[[0, 1, 2, 3]]],
                            "semantics": {
                                "surfaces": [{"type": "RoofSurface"}],
                                "values": [0],
                            },
                        }
                    ],
                }
            },
            "vertices": [[0, 0, 0], [10, 0, 0], [10, 10, 0], [0, 10, 0]],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            input_path = Path(tmp.name)
            json.dump(cityjson_data, tmp)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_cityjson(input_path, output_path)

            building_obj = result["CityObjects"]["test-building"]

            # Check existing attributes are preserved
            assert building_obj["attributes"]["existing_attr"] == "preserved"
            assert building_obj["attributes"]["year_built"] == 2020

            # Check new attribute was added
            assert "total_area_roof" in building_obj["attributes"]
            assert building_obj["attributes"]["total_area_roof"] == 100.0

        finally:
            input_path.unlink()
            output_path.unlink()

    def test_multiple_buildings(self):
        """Test processing file with multiple buildings."""
        cityjson_data = {
            "type": "CityJSON",
            "version": "2.0",
            "transform": {
                "scale": [1.0, 1.0, 1.0],
                "translate": [0.0, 0.0, 0.0],
            },
            "CityObjects": {
                "building-1": {
                    "type": "Building",
                    "geometry": [
                        {
                            "type": "MultiSurface",
                            "boundaries": [[[0, 1, 2, 3]]],
                            "semantics": {
                                "surfaces": [{"type": "RoofSurface"}],
                                "values": [0],
                            },
                        }
                    ],
                },
                "building-2": {
                    "type": "Building",
                    "geometry": [
                        {
                            "type": "MultiSurface",
                            "boundaries": [[[0, 1, 2, 3]]],
                            "semantics": {
                                "surfaces": [{"type": "RoofSurface"}],
                                "values": [0],
                            },
                        }
                    ],
                },
            },
            "vertices": [[0, 0, 0], [5, 0, 0], [5, 5, 0], [0, 5, 0]],
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            input_path = Path(tmp.name)
            json.dump(cityjson_data, tmp)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".city.json", delete=False
        ) as tmp:
            output_path = Path(tmp.name)

        try:
            result = process_cityjson(input_path, output_path)

            # Both buildings should have roof area calculated
            assert (
                "total_area_roof" in result["CityObjects"]["building-1"]["attributes"]
            )
            assert (
                "total_area_roof" in result["CityObjects"]["building-2"]["attributes"]
            )

            # Both should have area 5x5 = 25
            assert (
                result["CityObjects"]["building-1"]["attributes"]["total_area_roof"]
                == 25.0
            )
            assert (
                result["CityObjects"]["building-2"]["attributes"]["total_area_roof"]
                == 25.0
            )

        finally:
            input_path.unlink()
            output_path.unlink()
