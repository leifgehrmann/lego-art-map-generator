from typing import Tuple, Iterator, List

import math
import numpy

import random
from pathlib import Path

import click
from PIL import Image


def raster_random_iterator(
        width: int,
        height: int
) -> Iterator[Tuple[int, int]]:
    x, y, skipped = 0, 0, 0
    visited = numpy.zeros((width, height), dtype='bool')
    while skipped < width * height:
        if visited[x, y] == 1:
            skipped += 1
            offset = width + height - 1
            y = (y + math.floor((x + offset) / width)) % height
            x = (x + offset) % width
        else:
            skipped = 0
            yield x, y
            visited[x, y] = 1
            offset = random.randint(0, int(width))
            y = (y + math.floor((x + offset) / width)) % height
            x = (x + offset) % width


def get_neighbor_colors(
        image: Image.Image,
        color_map: List[Tuple[int, int, int]],
        x: int,
        y: int
) -> Iterator[int]:
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
            colors.append(color_map.index(image.getpixel((pos[0], pos[1]))))
        except ValueError:
            continue
    return colors


@click.command()
@click.argument(
    'overlay',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'sea',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
def render(overlay: str, sea: str, dst: str):
    overlay_filepath = Path(overlay)
    sea_filepath = Path(sea)
    output_filepath = Path(dst)

    sea_depth_colors = [
        (19, 183, 210),   # Cyan
        (0, 153, 150),    # Teal
        (0, 161, 55),     # Green
        (162, 197, 16),   # Olive
        (226, 202, 144),  # Beige
        (248, 172, 0),    # Yellow
        (238, 117, 0),    # Orange
        (237, 106, 112),  # Coral
    ]

    sea_depth_color_max_count = [
        1668,  # Cyan
        1956,  # Teal
        621,  # Green
        1106,  # Olive
        752,  # Beige
        619,  # Yellow
        625,  # Orange
        627  # Coral
    ]
    sea_depth_color_max_count = [
        1606,  # Cyan
        1878,  # Teal
        529,  # Green
        1019,  # Olive
        724,  # Beige
        598,  # Yellow
        229,  # Orange
        203  # Coral
    ]
    sea_depth_color_count = [
        1668,  # Cyan
        1956,  # Teal
        621,  # Green
        1106,  # Olive
        752,  # Beige
        619,  # Yellow
        625,  # Orange
        627  # Coral
    ]
    sea_depth_color_indexes = list(range(len(sea_depth_color_count)))

    # i:    0,   16,   32,   48,   64,   80,   96,  112,  128,  144,  160,  176,  192,  208,  224,  240
    sea_depth_color_weights = [
        [0.15, 0.15, 0.65, 0.65, 0.65, 0.65, 0.95, 8.09, 40.0, 1.30, 0.05, 0.10, 0.30, 0.30, 0.20, 0.10],  # noqa: E501 Cyan
        [0.01, 0.01, 0.01, 0.05, 0.10, 0.10, 0.20, 15.9, 99.0, 1.30, 0.05, 0.15, 0.15, 0.15, 0.15, 0.05],  # noqa: E501 Teal
        [0.00, 0.00, 0.02, 0.03, 0.03, 0.05, 99.0, 15.0, 0.20, 9.02, 0.15, 0.15, 0.05, 0.05, 0.05, 0.02],  # noqa: E501 Green
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50, 1.00, 9.00, 0.00, 0.00, 0.16, 0.18],  # noqa: E501 Olive
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.04, 1.15, 99.0, 0.00, 0.00, 0.18, 0.37],  # noqa: E501 Beige
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.01, 0.65, 40.0, 0.00, 0.00, 0.22, 0.18],  # noqa: E501 Yellow
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.15, 20.0, 0.00, 0.00, 0.07, 0.08],  # noqa: E501 Orange
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.15, 20.0, 0.00, 0.00, 0.04, 0.08],  # noqa: E501 Coral
    ]
    for weight_index in range(len(sea_depth_color_weights[0])):
        # Compute the total weight for each column
        weight_total = 0
        for color_index in range(len(sea_depth_color_weights)):
            weight_total += sea_depth_color_weights[color_index][weight_index]
        # Normalise the weights
        for color_index in range(len(sea_depth_color_weights)):
            sea_depth_color_weights[color_index][weight_index] /= weight_total

    def choose_sea_depth_color(
            sea_depth: int,
            neighbor_colors: Iterator[int]
    ) -> int:
        total_num_of_depth_weights = len(sea_depth_color_weights[0])
        depth_weight_index = min(math.floor(
            sea_depth / 255 * total_num_of_depth_weights
        ), total_num_of_depth_weights - 1)

        weights = [
            max(
                min(1.0, count / sea_depth_color_max_count[i]) ** 3 *
                (sea_depth_color_weights[i][depth_weight_index] + 0.0001) ** 2,
                0.0000000000001
            )
            for i, count in enumerate(sea_depth_color_count)
        ]

        # Reduce the probability of the color if one of its neighbors is the
        # same color.
        for neighbor_color in neighbor_colors:
            weights[neighbor_color] *= 0.8

        return random.choices(
            sea_depth_color_indexes,
            weights=weights
        )[0]

    overlay_image = Image.open(overlay_filepath.as_posix()).convert('RGB')
    sea_image = Image.open(sea_filepath.as_posix()).convert('RGB')

    pixel_i = 0
    for (x, y) in raster_random_iterator(
            overlay_image.width,
            overlay_image.height
    ):
        if overlay_image.getpixel((x, y)) == (0, 0, 0):
            sea_depth_val = sea_image.getpixel((x, y))[0]
            neighbor_colors_for_pos = get_neighbor_colors(
                overlay_image,
                sea_depth_colors,
                x,
                y
            )
            color_index = choose_sea_depth_color(
                sea_depth_val,
                neighbor_colors_for_pos
            )
            if sea_depth_color_count[color_index] > 0:
                sea_depth_color_count[color_index] -= 1
            selected_color = sea_depth_colors[color_index]
            overlay_image.putpixel(
                (x, y),
                selected_color
            )
            pixel_i += 1
            # overlay_image.putpixel(
            #     (x, y),
            #     (pixel_i & 255, ((pixel_i >> 8) & 255) * 16, 255)
            # )

    overlay_image.save(output_filepath.as_posix())


if __name__ == '__main__':
    render()
