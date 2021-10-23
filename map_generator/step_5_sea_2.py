import click
from pathlib import Path

from typing import Dict

from PIL import Image


def read_brightness_histogram_from_image(
        image: Image
) -> Dict[str, int]:
    """
    Get histogram of brightness values from sea depth image.
    """
    pass


# Get color distribution from distribution chart
# start,stop,color1,color2,color3,color4 but transposed
def read_brightness_proportions_from_file(
        file: Path
) -> Dict[str, Dict[str, float]]:
    pass


# Calculate expected number of tiles for each colors for each brightness value
# proportional to the distribution chart
def calculate_distribution_given_histogram(
        brightness_histogram: Dict[str, int],
        brightness_tile_proportions: Dict[str, Dict[str, float]]
) -> Dict[str, Dict[str, int]]:
    pass


# Get max tile values
def read_max_tile_count(
        file: Path
) -> Dict[str, int]:
    pass


def calculate_distribution_given_max_counts(
        brightness_distribution: Dict[str, Dict[str, int]],
        max_tile_count: Dict[str, int]
) -> Dict[str, Dict[str, int]]:
    """
    Distribute max color values proportionally to each brightness value, each
    different color at a time.

    For each color, if some buckets are not filled, pick a brightness bucket
    randomly that has not been filled, proportional to the number of tiles they
    have. If all buckets have been filled, pick any bucket randomly
    proportional to the number of tiles it already has.

    At the end we should have an array, indexed by brightness level, then
    indexed by color, with each value being the number of tiles

    :param brightness_distribution:
    :param max_tile_count:
    :return:
    """
    pass


@click.command()
@click.argument(
    'src',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'sea',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'tile_distribution',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'tile_count',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
def render(
        overlay: str,
        sea: str,
        tile_distribution: str,
        tile_count: str,
        dst: str
):
    # Iterate through the bitmap and distribute the tiles according to their
    # brightness level, and the number of tiles left in each bucket.
    pass
