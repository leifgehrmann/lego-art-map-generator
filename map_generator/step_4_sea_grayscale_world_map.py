from PIL import Image
from map_engraver.canvas.canvas_unit import CanvasUnit
from numpy import zeros, dtype
from pathlib import Path

import click
from geotiff import GeoTiff

from map_generator.lego_projection_transformer_builder import \
    LegoProjectionTransformerBuilder


@click.command()
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
def render(dst: str):
    # Load the world bathymetric map data
    gebco_tiff_path = Path('data/gebco_2021.tif')
    geo_tiff = GeoTiff(gebco_tiff_path.as_posix())

    canvas_width = CanvasUnit.from_px(128)
    canvas_height = CanvasUnit.from_px(80)
    canvas_shape = (int(canvas_height.px), int(canvas_width.px))
    # For each position on the map, lookup the bathymetric value at that exact
    # position and store in the array.
    lego_projection_transformer_builder = LegoProjectionTransformerBuilder(
        canvas_width,
        canvas_height
    )

    lego_to_wgs84_transformer = lego_projection_transformer_builder. \
        build_lego_to_wgs84()
    output_arr = zeros(shape=canvas_shape, dtype=dtype('uint8'))
    for output_y in range(output_arr.shape[0]):
        print(output_y)
        for output_x in range(output_arr.shape[1]):
            # if output_x % 4 != 0 or output_y % 4 != 0:
            #     continue
            # We want the center of the WGS84 bbox, so add 0.5 to the x and y
            lon, lat = lego_to_wgs84_transformer(
                output_x + 0.5,
                output_y + 0.5
            )
            output_arr[output_y][output_x] = geo_tiff.read_box(
                ((lon, lat), (lon, lat)), outer_points=1
            )[0][0] * 9

    # Convert the array to be a grayscale bitmap.
    output_filepath = Path(dst)
    Image \
        .fromarray(output_arr, mode='L') \
        .save(output_filepath.as_posix())


if __name__ == '__main__':
    render()
