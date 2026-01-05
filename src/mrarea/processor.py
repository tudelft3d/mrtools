"""CityJSON processing logic for calculating roof areas."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from .geometry import calculate_surface_area


def get_surface_semantic_type(
    surface_index: int | Tuple[int, int],
    semantics: Optional[Dict[str, Any]],
    geom_type: str,
) -> Optional[str]:
    """
    Get the semantic type for a surface.

    Args:
        surface_index: For Solid: (shell_idx, face_idx), for MultiSurface: face_idx
        semantics: The semantics object from geometry
        geom_type: 'Solid' or 'MultiSurface'

    Returns:
        Semantic type string (e.g., 'RoofSurface') or None if not found
    """
    if not semantics or "values" not in semantics or "surfaces" not in semantics:
        return None

    values = semantics["values"]
    surfaces = semantics["surfaces"]

    try:
        if geom_type == "Solid":
            # For Solid: values is nested [[shell_values]]
            shell_idx, face_idx = surface_index
            if shell_idx < len(values) and face_idx < len(values[shell_idx]):
                type_idx = values[shell_idx][face_idx]
                if type_idx is not None and type_idx < len(surfaces):
                    return surfaces[type_idx].get("type")

        elif geom_type == "MultiSurface":
            # For MultiSurface: values is flat [face_values]
            face_idx = surface_index
            if face_idx < len(values):
                type_idx = values[face_idx]
                if type_idx is not None and type_idx < len(surfaces):
                    return surfaces[type_idx].get("type")

    except (IndexError, KeyError, TypeError):
        return None

    return None


def extract_roof_surfaces(
    geometry: Dict[str, Any],
    vertices_global: List[List[int]],
    transform: Dict[str, List[float]],
) -> List[float]:
    """
    Extract all roof surface areas from a geometry object.

    Handles both 'Solid' and 'MultiSurface' geometry types.

    Args:
        geometry: A geometry object from a CityObject
        vertices_global: Global vertices array from CityJSON root
        transform: Transform object with scale and translate

    Returns:
        List of roof surface areas
    """
    geom_type = geometry.get("type")
    boundaries = geometry.get("boundaries", [])
    semantics = geometry.get("semantics")

    roof_areas = []

    if geom_type == "Solid":
        # Solid: boundaries[shell_idx][face_idx][ring_idx][vertex_idx]
        for shell_idx, shell in enumerate(boundaries):
            for face_idx, face in enumerate(shell):
                sem_type = get_surface_semantic_type(
                    (shell_idx, face_idx), semantics, geom_type
                )
                if sem_type == "RoofSurface":
                    area = calculate_surface_area(face, vertices_global, transform)
                    roof_areas.append(area)

    elif geom_type == "MultiSurface":
        # MultiSurface: boundaries[face_idx][ring_idx][vertex_idx]
        for face_idx, face in enumerate(boundaries):
            sem_type = get_surface_semantic_type(face_idx, semantics, geom_type)
            if sem_type == "RoofSurface":
                area = calculate_surface_area(face, vertices_global, transform)
                roof_areas.append(area)

    return roof_areas


def calculate_roof_area_for_object(
    obj_data: Dict[str, Any],
    vertices_global: List[List[int]],
    transform: Dict[str, List[float]],
) -> float:
    """
    Calculate total roof area for a CityObject.

    Args:
        obj_data: A CityObject from the CityObjects dictionary
        vertices_global: Global vertices array from CityJSON root
        transform: Transform object with scale and translate

    Returns:
        Total roof area in square units, or 0.0 if no roof surfaces found
    """
    geometries = obj_data.get("geometry", [])
    total_roof_area = 0.0

    for geometry in geometries:
        roof_areas = extract_roof_surfaces(geometry, vertices_global, transform)
        total_roof_area += sum(roof_areas)

    return total_roof_area


def process_cityjson(
    input_path: Path, output_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Process a CityJSON file and add roof area attributes.

    Loads the CityJSON file, calculates roof areas for all CityObjects,
    and adds the 'total_area_roof' attribute to each object.

    Args:
        input_path: Path to input CityJSON file
        output_path: Path to output file (if None, overwrites input)

    Returns:
        Modified CityJSON dictionary

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
        KeyError: If required CityJSON structure is missing
    """
    # Read the CityJSON file
    with open(input_path, "r", encoding="utf-8") as f:
        cityjson = json.load(f)

    # Validate basic structure
    if "CityObjects" not in cityjson:
        raise KeyError("Invalid CityJSON: missing 'CityObjects'")
    if "vertices" not in cityjson:
        raise KeyError("Invalid CityJSON: missing 'vertices'")

    # Extract global data
    vertices_global = cityjson["vertices"]
    transform = cityjson.get("transform", {"scale": [1.0, 1.0, 1.0], "translate": [0.0, 0.0, 0.0]})
    city_objects = cityjson["CityObjects"]

    # Process each CityObject
    for obj_id, obj_data in city_objects.items():
        # Calculate roof area
        roof_area = calculate_roof_area_for_object(obj_data, vertices_global, transform)

        # Add or update attributes
        if "attributes" not in obj_data:
            obj_data["attributes"] = {}

        obj_data["attributes"]["total_area_roof"] = roof_area

    # Write output
    output_file = output_path if output_path else input_path
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cityjson, f, indent=2)

    return cityjson
