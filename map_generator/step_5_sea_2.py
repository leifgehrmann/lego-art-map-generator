import csv
import random

import click
from pathlib import Path

from typing import Dict

from PIL import Image


def read_brightness_histogram_from_image(
        brightness_image_path: Path,
        mask_image_path: Path
) -> Dict[int, int]:
    """
    Get histogram of brightness values from sea depth image. In other words,
    count how many pixels the brightness_image has for every brightness level.
    """
    brightness_image = Image.open(
        brightness_image_path.as_posix()
    ).convert('RGB')
    mask_image = Image.open(
        mask_image_path.as_posix()
    ).convert('RGB')

    brightness_histogram = {}
    for y in range(brightness_image.height):
        for x in range(brightness_image.width):
            # Skip pixels where the mask image has non-zero content.
            if mask_image.getpixel((x, y)) != (0, 0, 0):
                continue

            # Increase the count for the measured brightness value.
            val = int(brightness_image.getpixel((x, y))[0])
            if val not in brightness_histogram:
                brightness_histogram[val] = 0
            brightness_histogram[val] += 1
    return brightness_histogram


def read_brightness_tile_proportion_from_csv(
        csv_path: Path
) -> Dict[int, Dict[str, float]]:
    """
    Reads the tile distribution for each brightness level from distribution
    chart.
    """
    proportions = {}
    row_count = 0
    brightness_ranges = []
    with open(csv_path.as_posix()) as file:
        for row in csv.reader(file, delimiter=',', skipinitialspace=True):
            row_count += 1
            if row_count == 1:
                brightness_ranges = row[1:]
                continue

            tile = row[0]
            brightness_proportions = row[1:]

            for brightness_proportion_i in range(len(brightness_proportions)):
                brightness_range_str = brightness_ranges[
                    brightness_proportion_i
                ]
                brightness_proportion = float(brightness_proportions[
                    brightness_proportion_i
                ])
                start_str, end_str = brightness_range_str.split('-')
                start = int(start_str)
                end = int(end_str)
                for brightness in range(start, end + 1):
                    if brightness not in proportions:
                        proportions[brightness] = {}
                    proportions[brightness][tile] = brightness_proportion

    # Normalise the proportions to be between 0 and 1
    for brightness, tile_proportions in proportions.items():
        tile_proportion_sum = sum(tile_proportions.values())
        for tile, proportion in tile_proportions.items():
            proportions[brightness][tile] = proportion / tile_proportion_sum

    return proportions


def calculate_distribution_given_histogram(
        brightness_histogram: Dict[int, int],
        brightness_tile_proportions: Dict[int, Dict[str, float]]
) -> Dict[int, Dict[str, int]]:
    """
    Calculate expected number of tiles for each colors for each brightness
    value proportional to the distribution chart.
    """
    distribution = {}
    for brightness, count in brightness_histogram.items():
        if brightness not in distribution:
            distribution[brightness] = {}
        tile_proportions = brightness_tile_proportions[brightness]

        for tile in random.choices(
            list(tile_proportions.keys()),
            weights=list(tile_proportions.values()),
            k=count
        ):
            if tile not in distribution[brightness]:
                distribution[brightness][tile] = 0
            distribution[brightness][tile] += 1

    return distribution


def read_max_tile_counts_from_csv(
        csv_path: Path
) -> Dict[str, int]:
    """
    Reads the max tile counts.
    """
    max_tile_counts = {}

    row_count = 0
    with open(csv_path.as_posix()) as file:
        for row in csv.reader(file, delimiter=',', skipinitialspace=True):
            row_count += 1
            if row_count == 1:
                continue

            tile = row[0]
            max_count = int(row[1])
            max_tile_counts[tile] = max_count

    return max_tile_counts


def calculate_distribution_given_max_counts(
        brightness_tile_distribution: Dict[int, Dict[str, int]],
        max_tile_count: Dict[str, int]
) -> Dict[int, Dict[str, int]]:
    """
    Distribute max color values proportionally to each brightness value, each
    different color at a time.

    For each color, if some buckets are not filled, pick a brightness bucket
    randomly that has not been filled, proportional to the number of tiles they
    have. If all buckets have been filled, pick any bucket randomly
    proportional to the number of tiles it already has.

    At the end we should have an array, indexed by brightness level, then
    indexed by color, with each value being the number of tiles
    """
    output = {}

    # Transpose the distribution dict for easy calculations later on.
    tile_brightness_distribution = {}
    for brightness, tile_distributions in brightness_tile_distribution.items():
        for tile, distribution in tile_distributions.items():
            if tile not in tile_brightness_distribution:
                tile_brightness_distribution[tile] = {}
            if brightness not in tile_brightness_distribution[tile]:
                tile_brightness_distribution[tile][brightness] = distribution

    return output


def render_image(
        overlay_image_path: Path,
        brightness_tile_distribution: Dict[int, Dict[str, int]],
        output_image_path: Path
):
    output_image = Image.open(
        overlay_image_path.as_posix()
    ).convert('RGB')

    # Todo

    output_image.save(output_image_path.as_posix())


@click.command()
@click.argument(
    'overlay_image',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'brightness_image',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'brightness_tile_proportion_csv',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'max_tile_counts_csv',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'output_image',
    nargs=1,
    type=click.Path(exists=False)
)
def render(
        overlay_image: str,
        brightness_image: str,
        brightness_tile_proportion_csv: str,
        max_tile_counts_csv: str,
        output_image: str
):
    # Iterate through the bitmap and distribute the tiles according to their
    # brightness level, and the number of tiles left in each bucket.
    brightness_histogram = \
        read_brightness_histogram_from_image(
            Path(brightness_image),
            Path(overlay_image)
        )

    brightness_tile_proportion = \
        read_brightness_tile_proportion_from_csv(
            Path(brightness_tile_proportion_csv)
        )

    max_tile_counts = read_max_tile_counts_from_csv(Path(max_tile_counts_csv))

    brightness_tile_expected_distribution = \
        calculate_distribution_given_histogram(
            brightness_histogram,
            brightness_tile_proportion
        )

    brightness_tile_actual_distribution = \
        calculate_distribution_given_max_counts(
            brightness_tile_expected_distribution,
            max_tile_counts
        )

    render_image(
        Path(overlay_image),
        brightness_tile_actual_distribution,
        Path(output_image)
    )
    pass


if __name__ == '__main__':
    render()
