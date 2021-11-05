#

# Visualize the bla bla
from pathlib import Path

import click
from PIL import Image

from map_generator.brightness_tile_proportions import BrightnessTileProportions


@click.command()
@click.argument(
    'proportions',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
def visualize(proportions, dst):
    brightness_count = BrightnessTileProportions.read_from_csv(
        Path(proportions)
    )

    brightness_range = 256
    max_height = 256

    img = Image.new('RGB', (brightness_range, max_height), color=0)
    for brightness in [i for i in sorted(brightness_count.keys())]:
        y_offset = 0
        for tile in [i for i in sorted(brightness_count[brightness].keys())]:
            rgb = tuple([int(b) for b in tile.split(',')])
            amount = int(brightness_count[brightness][tile] * 256)
            for y in range(y_offset, y_offset + amount):
                if y < img.height:
                    img.putpixel((brightness, y), rgb)
            y_offset += amount

    img.save(Path(dst).as_posix())


if __name__ == '__main__':
    visualize()
