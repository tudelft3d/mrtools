# mrtools

A Python CLI tool suite, made for the [MultiRoofs project](https://multiroofs.nweurope.eu/), for processing CityJSON files.

## Tools

### roofarea

The `roofarea` command processes CityJSON files containing Buildings (and BuildingParts) and adds a `total_area_roof` attribute to each CityObject. The value is calculated as the sum of areas of all surfaces semantically labeled as "RoofSurface".

If a building has no semantic information, `total_area_roof` is set to 0.0.


## Installation

Install the package in development mode:

```bash
uv pip install -e .
```

## Usage

Basic usage:

```bash
uv run mrtools roofarea input.city.json -o output.city.json
```

Verbose mode (shows processing details):

```bash
uv run mrtools roofarea input.city.json -o output.city.json --verbose
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

### Geometry Support

The tool handles both geometry types found in CityJSON:

- **Solid geometry** (e.g., Dutch 3D BAG): `boundaries[shell][face][ring][vertex]`
- **MultiSurface geometry** (e.g., Montreal dataset): `boundaries[face][ring][vertex]`


## Project Structure

```
mrtools/
├── src/
│   └── mrtools/
│       ├── __init__.py         # Package initialization
│       ├── cli.py              # Typer CLI interface with subcommands
│       ├── processor.py        # CityJSON processing logic
│       └── geometry.py         # Geometric calculations
├── data/                       # Sample CityJSON files
│   ├── 3dbag_b2.city.json
│   └── montréal_b4.city.json
├── tests/                      # Test files
├── pyproject.toml              # Project configuration
└── README.md
```

## Requirements

`pip install typer cjio`


- Python >= 3.13
- typer >= 0.12.0
- cjio >= 0.10.1
- pytest >= 9.0.2 (dev dependency)
