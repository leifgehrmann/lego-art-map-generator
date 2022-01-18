from PIL import Image
from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.layout.background import Background
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from pathlib import Path

import click
from shapely.geometry import Point


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
def render(
        src: str,
        dst: str
):
    input_filepath = Path(src)
    output_filepath = Path(dst)
    shadow_color = (0, 53, 91)

    # Read the src image.
    image = Image.open(input_filepath.as_posix()).convert('RGB')

    # Create a canvas.
    canvas_builder = CanvasBuilder()
    canvas_builder.set_pixel_scale_factor(8)
    canvas_builder.set_size(
        CanvasUnit.from_px(image.width),
        CanvasUnit.from_px(image.height)
    )
    canvas_builder.set_path(output_filepath)
    canvas = canvas_builder.build()

    # Set the background to black.
    background = Background()
    background.color = (0, 0, 0, 1)
    background.draw(canvas)

    # For each pixel we draw the pixel as a circle onto a canvas with 8x
    # enlargement.
    polygon_drawer = PolygonDrawer()
    for y in range(image.height):
        for x in range(image.width):
            color = image.getpixel((x, y))
            image.putpixel((x, y), shadow_color)

            x_pt = CanvasUnit.from_px(x + 0.5).pt
            y_pt = CanvasUnit.from_px(y + 0.5).pt
            size_pt = CanvasUnit.from_px(0.475).pt
            polygon_drawer.geoms = [
                Point(x_pt, y_pt).buffer(size_pt)
            ]
            polygon_drawer.fill_color = (
                color[0]/255,
                color[1]/255,
                color[2]/255,
                1
            )
            polygon_drawer.draw(canvas)

    # Save the canvas
    canvas.close()
    pass


if __name__ == '__main__':
    render()
