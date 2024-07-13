from pathlib import Path
from typing import List

import click
from PIL import Image

# Load image
from numpy import zeros, dtype, uint16
from numpy import asarray, array


def get_neighbors(x: int, y: int, source) -> List[int]:
    source_height, source_width = source.shape
    n = []
    for n_x_o in (-1, 0, 1):
        for n_y_o in (-1, 0, 1):
            if n_x_o == 0 and n_y_o == 0:
                continue
            n_y = (y + n_y_o) % source_height
            n_x = (x + n_x_o) % source_width
            n.append(source[n_y, n_x])
    return n


# Filter function
def custom_kernel_filter(x: int, y: int, source) -> int:
    c_val = source[y, x]
    neighbors = get_neighbors(x, y, source)
    n_sum = sum(array(neighbors).astype(uint16))
    n_val = n_sum / float(len(neighbors))
    if n_val > c_val * 1.15:
        return 0
    elif n_val < c_val * 0.85:
        return 255
    if c_val > 125:
        return 255
    return 0


def dither_filter(x: int, y: int, source) -> int:
    return source[y, x]


def threshold_filter(x: int, y: int, source) -> int:
    if source[y, x] > 128:
        return 255
    return 0


@click.command()
@click.argument(
    'src',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
@click.option(
    "--mode",
    required=True,
    type=click.Choice(
        ['threshold', 'dither', 'custom_1'],
        case_sensitive=False
    ))
def convert_grayscale_to_1bit(src: str, dst: str, mode: str):
    input_filepath = Path(src)
    output_filepath = Path(dst)

    # Convert to numpy, and get single-channel color
    input_rgb = asarray(Image.open(input_filepath.as_posix()))
    input_arr = input_rgb[:, :, 0]

    # Apply filter for each pixel on the map
    output_arr = zeros(shape=input_arr.shape, dtype=dtype('uint8'))

    if mode == 'threshold':
        filter_func = threshold_filter
    elif mode == 'dither':
        filter_func = dither_filter
    elif mode == 'custom_1':
        filter_func = custom_kernel_filter
    else:
        raise Exception('Please specify a mode')

    for output_y in range(output_arr.shape[0]):
        for output_x in range(output_arr.shape[1]):
            output_arr[output_y][output_x] = filter_func(
                output_x,
                output_y,
                input_arr
            )

    # Output the image
    # Numpy does not support 1-bit arrays, so we have to resort to first
    # creating the image as a 8-bit image, then convert to 1-bit.
    Image\
        .fromarray(output_arr, mode='L')\
        .convert('1')\
        .save(output_filepath.as_posix())


if __name__ == '__main__':
    convert_grayscale_to_1bit()
