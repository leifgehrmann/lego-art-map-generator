import math

from geotiff.geotiff import BoundaryNotInTifError
from typing import List, Tuple

from PIL import Image
from map_engraver.canvas.canvas_unit import CanvasUnit
from numpy import zeros, dtype
from pathlib import Path

import click
from geotiff import GeoTiff

from map_generator.lego_projection_transformer_builder import \
    LegoProjectionTransformerBuilder


Coord = Tuple[float, float]


def retrieve_geotiff_paths() -> List[Path]:
    data_dir = Path('data/gebco_2021_sub_ice_topo_geotiff/')
    geotiffs = [
        'gebco_2021_sub_ice_topo_n0.0_s-90.0_w0.0_e90.0.tif',
        'gebco_2021_sub_ice_topo_n0.0_s-90.0_w90.0_e180.0.tif',
        'gebco_2021_sub_ice_topo_n0.0_s-90.0_w-90.0_e0.0.tif',
        'gebco_2021_sub_ice_topo_n0.0_s-90.0_w-180.0_e-90.0.tif',
        'gebco_2021_sub_ice_topo_n90.0_s0.0_w0.0_e90.0.tif',
        'gebco_2021_sub_ice_topo_n90.0_s0.0_w90.0_e180.0.tif',
        'gebco_2021_sub_ice_topo_n90.0_s0.0_w-90.0_e0.0.tif',
        'gebco_2021_sub_ice_topo_n90.0_s0.0_w-180.0_e-90.0.tif'
    ]
    return list(map(lambda geotiff: data_dir.joinpath(geotiff), geotiffs))


def retrieve_geotiffs() -> List[GeoTiff]:
    return list(map(
        lambda geotiff_path: GeoTiff(geotiff_path.as_posix()),
        retrieve_geotiff_paths()
    ))


def is_coord_in_geotiff(coord: Coord, geotiff: GeoTiff) -> bool:
    try:
        return len(geotiff.get_int_box(
            (coord, coord), outer_points=1
        )) == 2
    except BoundaryNotInTifError:
        return False


def lookup_coord_in_geotiffs(coord: Coord, geotiffs: List[GeoTiff]) -> GeoTiff:
    for geotiff in geotiffs:
        if is_coord_in_geotiff(coord, geotiff):
            return geotiff
    raise Exception(
        'Failed to lookup geotiff for (%f, %f)' % (coord[0], coord[1])
    )


@click.command()
@click.argument(
    'mask',
    nargs=1,
    type=click.Path(exists=True)
)
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
def render(mask: str, dst: str):
    # Load the land + shadow mask map, to skip cells we know we don't need to
    # render over.
    mask = Image.open(Path(mask).as_posix()).convert('RGB')

    # Load the world bathymetric map data
    geotiffs = retrieve_geotiffs()

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
    current_geotiff = None
    for output_y in range(output_arr.shape[0]):
        print(output_y)
        for output_x in range(output_arr.shape[1]):
            # Skip pixels that will already be covered by the land + shadow map
            if mask.getpixel((output_x, output_y)) != (0, 0, 0):
                output_arr[output_y][output_x] = 255
                continue

            # We want the center of the WGS84 bbox, so add 0.5 to the x and y
            coord = lego_to_wgs84_transformer(
                output_x + 0.5,
                output_y + 0.5
            )

            # Lookup the correct geotiff to read
            if (
                    current_geotiff is None or
                    not is_coord_in_geotiff(coord, current_geotiff)
            ):
                current_geotiff = lookup_coord_in_geotiffs(coord, geotiffs)

            # Read from the geotiff and store in the output array
            value = (current_geotiff.read_box(
                (coord, coord), outer_points=1
            )[0][0])
            value = int(255 - math.ceil((min(0, value) / -10511.0) * 255))
            output_arr[output_y][output_x] = value

    # Convert the array to be a grayscale bitmap.
    output_filepath = Path(dst)
    Image \
        .fromarray(output_arr, mode='L') \
        .save(output_filepath.as_posix())


if __name__ == '__main__':
    render()
