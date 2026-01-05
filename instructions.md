Build a CLI with Python that takes an input a CityJSON files containing Buildings (which can have BuildingParts) and add to each CityObject an attribute "total_area_roof" to each where the sum of the areas of the surfaces that are semantically "RoofSurface".

The schema of CityJSON are there:
https://3d.bk.tudelft.nl/schemas/cityjson/2.0.1/

It's possible that a building has no semantic and you cannot find which surfaces are the roofs or not, in which case the "total_area_roof" is 0.0.

Please use JSON parser from standard lib to read/write, and use Typer as the CLI builder tool.
