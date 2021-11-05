import csv
import random

import click
from pathlib import Path

from typing import Dict, Tuple, Iterator, List

from PIL import Image

from map_generator.brightness_tile_proportions import BrightnessTileProportions


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

        # Multiply the percentage by a thousand so we can get a representative
        # sample of tiles.
        tile_counts = [int(x * 1000) for x in tile_proportions.values()]

        for tile in random.sample(
                list(tile_proportions.keys()),
                counts=tile_counts,
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
        max_tile_counts: Dict[str, int]
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
    brightnesses = brightness_tile_distribution.keys()
    tiles = max_tile_counts.keys()

    for brightness in brightnesses:
        output[brightness] = {}

    used_brightnesses_count = {}
    for brightness in brightnesses:
        used_brightnesses_count[brightness] = 0

    used_tiles_count = {}
    for tile in tiles:
        used_tiles_count[tile] = 0

    total_tiles_to_use = 0
    # Transpose the distribution dict for easy calculations later on. And also
    # count how many tiles we need to distribute.
    tile_brightness_distribution = {}
    for brightness, tile_distributions in brightness_tile_distribution.items():
        for tile, distribution in tile_distributions.items():
            if tile not in tile_brightness_distribution:
                tile_brightness_distribution[tile] = {}
            if brightness not in tile_brightness_distribution[tile]:
                tile_brightness_distribution[tile][brightness] = distribution
            total_tiles_to_use += distribution

    tiles = max_tile_counts.keys()
    used_tiles_total = 0
    while used_tiles_total < total_tiles_to_use:
        # Select a tile based on the initial expected distribution
        tile_weights = {}
        for tile in tiles:
            # The estimated tile count
            est_tile_count = sum(tile_brightness_distribution[tile].values())
            used_tile_count = used_tiles_count[tile]
            max_tile_count = max_tile_counts[tile]
            percent_left_over = 1 - used_tile_count / max_tile_count
            # The math here is a bit dubious... The probability of selecting
            # the same tile will decrease as the percent of each tile being
            # used increases, but not at a rate similar to randomly choosing
            # from a place without replacement.
            tile_weights[tile] = percent_left_over * est_tile_count

        selected_tile = random.choices(
            list(tile_weights.keys()), weights=list(tile_weights.values())
        )[0]

        # Now select a brightness "bucket" that is not filled, and also has

        brightness_weights = {}
        for brightness, tile_distributions in \
                brightness_tile_distribution.items():
            est_count = 0.0001
            if selected_tile in brightness_tile_distribution[brightness]:
                est_count = \
                    brightness_tile_distribution[brightness][selected_tile]
            max_count = sum(brightness_tile_distribution[brightness].values())
            used_count = used_brightnesses_count[brightness]
            percent_left_over = 1 - used_count / max_count
            brightness_weights[brightness] = percent_left_over * est_count

        selected_brightness = random.choices(
            list(brightness_weights.keys()),
            weights=list(brightness_weights.values())
        )[0]

        used_tiles_count[selected_tile] += 1
        used_brightnesses_count[selected_brightness] += 1
        used_tiles_total += 1

        if selected_tile not in output[selected_brightness]:
            output[selected_brightness][selected_tile] = 0
        output[selected_brightness][selected_tile] += 1

    return output


def raster_odd_iterator(
        width: int,
        height: int
) -> Iterator[Tuple[int, int]]:
    for i_h in range(height):
        for i_w in range(int(width / 2)):
            x = (i_w * 2 + i_h % 2)
            y = i_h
            if x < width:
                yield x, y
    for i_h in range(height):
        for i_w in range(int(width / 2)):
            x = (i_w * 2 + (i_h + 1) % 2)
            y = i_h
            if x < width:
                yield x, y


def get_neighboring_colors(
        image: Image,
        x: int,
        y: int
) -> List[Tuple[int, int, int]]:
    colors = []
    neighbor_positions = []
    if x + 1 < image.width:
        neighbor_positions.append(((x + 1) % image.width, y))
    if x - 1 >= 0:
        neighbor_positions.append(((x - 1) % image.width, y))
    if y + 1 < image.height:
        neighbor_positions.append((x, (y + 1) % image.width))
    if y - 1 >= 0:
        neighbor_positions.append((x, (y - 1) % image.width))
    for pos in neighbor_positions:
        try:
            colors.append(image.getpixel((pos[0], pos[1])))
        except ValueError:
            continue
    return colors


def render_image(
        brightness_image_path: Path,
        overlay_image_path: Path,
        brightness_tile_distribution: Dict[int, Dict[str, int]],
        output_image_path: Path
):
    brightness_image = Image.open(
        brightness_image_path.as_posix()
    ).convert('RGB')
    output_image = Image.open(
        overlay_image_path.as_posix()
    ).convert('RGB')

    for x, y in raster_odd_iterator(output_image.width, output_image.height):
        # Skip pixels where the image already has content.
        if output_image.getpixel((x, y)) != (0, 0, 0):
            continue
        brightness = brightness_image.getpixel((x, y))[0]
        tiles = list(brightness_tile_distribution[brightness].keys())
        tile_weights = list(
            brightness_tile_distribution[brightness].values()
        )

        tile = random.choices(tiles, weights=tile_weights, k=1)[0]
        color = tuple([int(x) for x in tile.split(',')])

        neighbor_colors = get_neighboring_colors(output_image, x, y)
        # Re-roll selection if more than two neighboring tiles are the same
        # color.
        if len(list(filter(lambda c: c == color, neighbor_colors))) > 1:
            tile = random.choices(tiles, weights=tile_weights, k=1)[0]
            color = tuple([int(x) for x in tile.split(',')])
            neighbor_colors = get_neighboring_colors(output_image, x, y)

        if len(list(filter(lambda c: c == color, neighbor_colors))) > 1:
            tile = random.choices(tiles, weights=tile_weights, k=1)[0]
            color = tuple([int(x) for x in tile.split(',')])

        brightness_tile_distribution[brightness][tile] -= 1

        output_image.putpixel((x, y), color)

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

    brightness_tile_proportion = BrightnessTileProportions.read_from_csv(
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
        Path(brightness_image),
        Path(overlay_image),
        brightness_tile_actual_distribution,
        Path(output_image)
    )
    pass


if __name__ == '__main__':
    render()
