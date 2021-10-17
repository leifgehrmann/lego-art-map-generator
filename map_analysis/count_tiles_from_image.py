from pathlib import Path

import click
from PIL import Image


def get_tile_name_alias(tile_name: str) -> str:
    tile_name_alias = {
        '255,255,255': '01 - White',
        '0,53,91': '02 - Navy',
        '19,183,210': '03 - Cyan',
        '0,153,150': '04 - Teal',
        '0,161,55': '05 - Green',
        '162,197,16': '06 - Olive',
        '226,202,144': '07 - Beige',
        '248,172,0': '08 - Yellow',
        '238,117,0': '09 - Orange',
        '237,106,112': '10 - Coral',
    }
    if tile_name in tile_name_alias:
        return tile_name_alias[tile_name]
    return tile_name


@click.command()
@click.argument(
    'src',
    nargs=1,
    type=click.Path(exists=True)
)
def count(src):
    tile_count = {}
    total_count = 0

    input_filepath = Path(src)

    image = Image.open(input_filepath.as_posix()).convert('RGB')

    for y in range(image.height):
        for x in range(image.width):
            total_count += 1
            tile_name = "%d,%d,%d" % image.getpixel((x, y))
            tile_name = get_tile_name_alias(tile_name)
            if tile_name not in tile_count:
                tile_count[tile_name] = 0
            tile_count[tile_name] += 1

    # Print out the totals, sorted alphabetically
    for tile_name in [i for i in sorted(tile_count.keys())]:
        print('{:<15}{:>5}'.format(tile_name + ':', tile_count[tile_name]))
    print('{:<15}{:>5}'.format('total:', total_count))


if __name__ == '__main__':
    count()
