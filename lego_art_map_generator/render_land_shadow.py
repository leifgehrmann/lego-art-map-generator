from pathlib import Path

import click
from PIL import Image


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
def render(src: str, dst: str):
    input_filepath = Path(src)
    output_filepath = Path(dst)
    shadow_color = (0, 53, 91)

    image = Image.open(input_filepath.as_posix()).convert('RGB')

    for y in range(image.height):
        land_ahoy = False
        for x in range(image.width):
            if image.getpixel((x, y))[0] == 255:
                land_ahoy = True
            elif land_ahoy:
                image.putpixel((x, y), shadow_color)
                land_ahoy = False

    image.save(output_filepath.as_posix())


if __name__ == '__main__':
    render()
