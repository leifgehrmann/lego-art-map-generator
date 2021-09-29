from pathlib import Path
from typing import List

from PIL import Image

# Load image
from numpy import zeros, dtype
from numpy import asarray

output_path = Path(__file__).parent.parent.joinpath('output')
output_path.mkdir(parents=True, exist_ok=True)
input_filepath = output_path.joinpath('land_grayscale.png')
output_filepath = output_path.joinpath('land_kernel.png')

# Convert to numpy, and get single-channel color
input_rgb = asarray(Image.open(input_filepath.as_posix()))
input_arr = input_rgb[:, :, 0]


# Utility functions
def get_neighbors(x: int, y: int, source) -> List[int]:
    source_height, source_width = source.shape
    n = []
    for n_x_o in (-1, 0, 1):
        for n_y_o in (-1, 0, 1):
            if n_x_o == 0 and n_y_o == 0:
                continue
            n_y = (x + n_y_o) % source_height
            n_x = (y + n_x_o) % source_width
            n.append(source[n_y, n_x])
    return n


# Filter function
def one_bit_filter(x: int, y: int, source) -> int:
    c_val = source[y, x]
    if c_val >= 250:
        return 255
    neighbors = get_neighbors(x, y, source)
    adjacent_above_threshold = 255 * 0.5
    adjacent_below_threshold = 255 * 0.5
    adjacent_above_count = 0
    adjacent_below_count = 0
    for n_val in neighbors:
        if n_val > adjacent_above_threshold:
            adjacent_above_count += 1
        if n_val < adjacent_below_threshold:
            adjacent_below_count += 1
    if c_val > adjacent_above_threshold and adjacent_above_count > 6:
        return 255
    if c_val > adjacent_below_threshold and adjacent_below_count > 6:
        return 255

    return 0


# Apply filter for each pixel on the map
output_arr = zeros(shape=input_arr.shape, dtype=dtype('uint8'))
for output_y in range(output_arr.shape[0]):
    for output_x in range(output_arr.shape[1]):
        output_arr[output_y][output_x] = one_bit_filter(
            output_x,
            output_y,
            input_arr
        )

print(output_arr)

# Save image
Image\
    .fromarray(output_arr, mode='L')\
    .convert('1')\
    .save(output_filepath.as_posix())
