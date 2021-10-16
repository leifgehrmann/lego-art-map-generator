from pathlib import Path

import click
from PIL import Image


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
        (19, 183, 210),
        (0, 153, 150),
        (0, 161, 55),
        (162, 197, 16),
        (226, 202, 144),
        (248, 172, 0),
        (238, 117, 0),
        (237, 106, 112),
    ]
    sea_depth_color_weights = (
        1606,
        1878,
        529,
        1019,
        724,
        598,
        229,
        203
    )

    overlay_image = Image.open(overlay_filepath.as_posix()).convert('RGB')
    sea_image = Image.open(sea_filepath.as_posix()).convert('RGB')
    weight_range = sum(sea_depth_color_weights)

    for y in range(overlay_image.height):
        for x in range(overlay_image.width):
            if overlay_image.getpixel((x, y)) == (0, 0, 0):
                color_weight = sea_image.getpixel((x, y))[0]/255 * weight_range
                color_index = 0
                while len(sea_depth_color_weights) != color_index and color_weight > sea_depth_color_weights[color_index]:
                    color_weight -= sea_depth_color_weights[color_index]
                    color_index += 1
                selected_color = sea_depth_colors[color_index - 1]
                overlay_image.putpixel(
                    (x, y),
                    selected_color
                )

    overlay_image.save(output_filepath.as_posix())


if __name__ == '__main__':
    render()
