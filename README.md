# mrarea

A Python CLI tool that calculates roof areas for CityJSON buildings.

## Description

`mrarea` processes CityJSON files containing Buildings (and BuildingParts) and adds a `total_area_roof` attribute to each CityObject. The value is calculated as the sum of areas of all surfaces semantically labeled as "RoofSurface".

If a building has no semantic information, `total_area_roof` is set to 0.0.

## Features

- ✅ Processes CityJSON 2.0 files
- ✅ Handles both `Solid` and `MultiSurface` geometry types
- ✅ Supports Buildings with BuildingParts
- ✅ Uses Newell's method for accurate 3D polygon area calculation
- ✅ Gracefully handles missing semantic information

## Installation

Using uv (recommended):

```bash
uv add typer
```

Or install the package in development mode:

```bash
uv pip install -e .
```

## Usage

Basic usage (overwrites input file):

```bash
uv run mrarea input.city.json
```

Specify an output file:

```bash
uv run mrarea input.city.json -o output.city.json
```

Verbose mode (shows processing details):

```bash
uv run mrarea input.city.json --verbose
```

### Example Output

```
Processing: data/3dbag_b2.city.json
✓ Processed 4 CityObjects
  NL.IMBAG.Pand.0503100000028341-0 (BuildingPart): 186.71 m²
  NL.IMBAG.Pand.0503100000028341 (Building): 0.00 m²
  NL.IMBAG.Pand.0503100000031927-0 (BuildingPart): 233.79 m²
  ... and 1 more objects
✓ Output written to: data/3dbag_b2_output.city.json
```

## How It Works

1. **Loads CityJSON file** using Python's standard library JSON parser
2. **Identifies roof surfaces** by checking semantic labels for "RoofSurface" type
3. **Calculates areas** using Newell's method for 3D polygon area calculation
4. **Adds attribute** `total_area_roof` to each CityObject's attributes
5. **Writes output** back to file (or specified output file)

### Geometry Support

The tool handles both geometry types found in CityJSON:

- **Solid geometry** (e.g., Dutch 3D BAG): `boundaries[shell][face][ring][vertex]`
- **MultiSurface geometry** (e.g., Montreal dataset): `boundaries[face][ring][vertex]`

### Area Calculation

Uses **Newell's method** for calculating 3D polygon areas, which:
- Works for non-planar polygons
- Handles any orientation in 3D space
- Is numerically stable

## Project Structure

```
mrarea/
├── src/
│   └── mrarea/
│       ├── __init__.py         # Package initialization
│       ├── cli.py              # Typer CLI interface
│       ├── processor.py        # CityJSON processing logic
│       └── geometry.py         # Geometric calculations
├── data/                       # Sample CityJSON files
│   ├── 3dbag_b2.city.json
│   └── montréal_b4.city.json
├── pyproject.toml              # Project configuration
└── README.md
```

## Requirements

- Python >= 3.13
- typer >= 0.12.0

## License

See project license file.

## References

- [CityJSON Specifications](https://www.cityjson.org/)
- [CityJSON 2.0.1 Schema](https://3d.bk.tudelft.nl/schemas/cityjson/2.0.1/)
