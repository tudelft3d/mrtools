"""Command-line interface for mrarea."""

import typer
from pathlib import Path
from typing import Optional
from .processor import process_cityjson

app = typer.Typer(
    help="Calculate roof areas for CityJSON buildings and add total_area_roof attributes."
)


@app.command()
def main(
    input_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to input CityJSON file",
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Path to output file (default: overwrites input file)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
) -> None:
    """
    Process a CityJSON file and add roof area attributes to all CityObjects.

    The tool calculates the total area of all surfaces semantically labeled as
    "RoofSurface" for each CityObject and adds this as a 'total_area_roof'
    attribute.

    If a building has no semantic information, total_area_roof is set to 0.0.
    """
    try:
        if verbose:
            typer.echo(f"Processing: {input_file}")

        # Process the file
        cityjson = process_cityjson(input_file, output_file)

        # Report statistics if verbose
        if verbose:
            num_objects = len(cityjson.get("CityObjects", {}))
            typer.echo(f"✓ Processed {num_objects} CityObjects")

            # Show some examples
            for i, (obj_id, obj_data) in enumerate(
                cityjson.get("CityObjects", {}).items()
            ):
                if i >= 3:  # Show only first 3
                    break
                roof_area = obj_data.get("attributes", {}).get("total_area_roof", 0.0)
                obj_type = obj_data.get("type", "Unknown")
                typer.echo(
                    f"  {obj_id} ({obj_type}): {roof_area:.2f} m²"
                )

            if num_objects > 3:
                typer.echo(f"  ... and {num_objects - 3} more objects")

        output_path = output_file if output_file else input_file
        typer.echo(f"✓ Output written to: {output_path}")

    except FileNotFoundError:
        typer.echo(f"Error: File not found: {input_file}", err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"Error: Invalid CityJSON file: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
