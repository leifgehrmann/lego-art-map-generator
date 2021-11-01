from pathlib import Path
from typing import Dict

import click
import csv
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


def save_csv(
        tile_count: Dict[str, Dict[int, int]],
        tile_total_count: Dict[int, int],
        dst_path: Path
) -> None:
    with open(dst_path.as_posix(), 'w', newline='') as dst_file:
        writer = csv.writer(dst_file)

        # Print out headers
        headers = ['tile']
        headers.extend(range(2 ** 8))
        writer.writerow(headers)

        # Print out full totals
        row = ['Total']
        for sea_value in range(2 ** 8):
            if sea_value not in tile_total_count:
                row.append(0)
            else:
                row.append(tile_total_count[sea_value])
        writer.writerow(row)

        # Print out the totals, sorted alphabetically
        for tile_name in [i for i in sorted(tile_count.keys())]:
            row = [tile_name]
            for sea_value in range(2 ** 8):
                if sea_value not in tile_count[tile_name]:
                    row.append(0)
                else:
                    row.append(tile_count[tile_name][sea_value])
            writer.writerow(row)


@click.command()
@click.argument(
    'tile',
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
@click.option(
    "--image/--csv",
    default=False,
    help='Output a CSV or an image'
)
def count(tile, sea, dst, image):
    tile_count = {}
    tile_total_count = {}

    tile_filepath = Path(tile)
    sea_filepath = Path(sea)

    tile_image = Image.open(tile_filepath.as_posix()).convert('RGB')
    sea_image = Image.open(sea_filepath.as_posix()).convert('RGB')

    for y in range(tile_image.height):
        for x in range(tile_image.width):
            tile_name = "%d,%d,%d" % tile_image.getpixel((x, y))
            sea_value = sea_image.getpixel((x, y))[0]
            tile_name = get_tile_name_alias(tile_name)
            if tile_name not in tile_count:
                tile_count[tile_name] = {}
            if sea_value not in tile_count[tile_name]:
                tile_count[tile_name][sea_value] = 0
            tile_count[tile_name][sea_value] += 1

            if sea_value not in tile_total_count:
                tile_total_count[sea_value] = 0
            tile_total_count[sea_value] += 1

    if image:
        pass
    else:
        save_csv(
            tile_count,
            tile_total_count,
            Path(dst)
        )


if __name__ == '__main__':
    count()
