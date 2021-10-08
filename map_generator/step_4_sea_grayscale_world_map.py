from pathlib import Path
from typing import List, Tuple

import click


class GeoBbox:
    def __init__(self, ):


def read_geotiff_bbox(image: Path) -> :


def read_geotiff_bboxes(images: List[Path])


def is_coord_in_bbox(wgs84_coord: Tuple[float, float]):



@click.command()
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
def render(dst: str):
    # Load the world bathymetric map data
    # For each position on the map, lookup the bathymetric value at that exact
    # position and store in the array.
    # Todo: If none is found, fill in a value ideally using a non-random algo?
    # Convert the array to be a grayscale bitmap.
    output_filepath = Path(dst)


if __name__ == '__main__':
    render()
