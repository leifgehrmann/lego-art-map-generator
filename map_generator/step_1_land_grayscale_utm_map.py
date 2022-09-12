from pathlib import Path
from typing import List, Tuple

import cairocffi
import click
import shapefile
from map_engraver.canvas import CanvasBuilder

from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from map_engraver.drawable.layout.background import Background
from shapely import ops
from shapely.geometry import shape, Polygon
from shapely.geometry.base import BaseGeometry

from utm_projection_transformer_builder import \
    UtmProjectionTransformerBuilder


def parse_size(size: str) -> Tuple[int, int]:
    split_size = size.split(',')

    if len(split_size) != 2:
        raise ValueError(
            'Unexpected size format. Expected 2, found %s' % len(split_size)
        )

    if not (0 < int(split_size[0])) or not (0 < int(split_size[1])):
        raise ValueError(
            'Unexpected size format. Expected positive integers'
        )

    return int(split_size[0]), int(split_size[1])


def parse_center(center: str) -> Tuple[float, float]:
    split_center = center.split(',')

    if len(split_center) != 2:
        raise ValueError(
            'Unexpected center coordinate format. '
            'Expected 2, found %s' % len(split_center)
        )

    longitude = float(split_center[0])
    latitude = float(split_center[1])
    if not (-180 < longitude < 180):
        raise ValueError(
            'Unexpected center longitude. '
            'Expected value between -180,180, found %f' % longitude
        )
    if not (-90 < latitude < 90):
        raise ValueError(
            'Unexpected center latitude. '
            'Expected value between -90,90, found %f' % latitude
        )

    return longitude, latitude


@click.command()
@click.argument(
    'dst',
    nargs=1,
    type=click.Path(exists=False)
)
@click.option(
    "--aliased/--anti-aliased",
    default=False,
    help='Disables anti-aliasing when rendering the image.'
)
@click.option(
    "--size",
    help='The width,height of the map in pixels.'
)
@click.option(
    "--center",
    help='The map latitude,longitude of the center position.'
)
@click.option(
    "--scale",
    help='The map scale, where a meter.'
)
@click.option(
    "--rotation",
    help='The rotation around the center of the map in degrees.'
)
@click.option(
    "--pixel-scale-factor",
    default=1,
    help='Controls the size of the image.'
)
def render(
        dst: str,
        aliased: bool,
        size: str,
        center: str,
        scale: str,
        rotation: str,
        pixel_scale_factor: int
):
    # Specify the files to load, and where to save
    data_path = Path(__file__).parent.parent.joinpath('data')
    land_shape_path = data_path.joinpath('ne_10m_land/ne_10m_land.shp')
    lake_shape_path = data_path.joinpath('ne_10m_lakes/ne_10m_lakes.shp')
    canvas_path = Path(dst)
    canvas_path.unlink(missing_ok=True)

    canvas_size_in_pixels = parse_size(size)
    center_coordinate = parse_center(center)

    # Create the canvas
    canvas_builder = CanvasBuilder()
    canvas_builder.set_path(canvas_path)
    canvas_width = CanvasUnit.from_px(canvas_size_in_pixels[0])
    canvas_height = CanvasUnit.from_px(canvas_size_in_pixels[1])
    canvas_builder.set_size(canvas_width, canvas_height)
    canvas_builder.set_pixel_scale_factor(pixel_scale_factor)
    canvas = canvas_builder.build()

    if aliased:
        canvas.context.set_antialias(cairocffi.ANTIALIAS_NONE)

    # Read world map shapefile
    def parse_shapefile(shapefile_path: Path):
        shapefile_collection = shapefile.Reader(shapefile_path.as_posix())
        shapely_objects = []
        for shape_record in shapefile_collection.shapeRecords():
            shapely_objects.append(shape(shape_record.shape.__geo_interface__))
        return shapely_objects

    land_shapes = parse_shapefile(land_shape_path)
    lake_shapes = parse_shapefile(lake_shape_path)

    utm_projection_transformer_builder = UtmProjectionTransformerBuilder(
        canvas_width,
        canvas_height,
        center_coordinate[0],
        center_coordinate[1],
        float(scale),
        float(rotation)
    )

    # We need to cull polygons outside of the bbox, which this thing achieves
    bbox = utm_projection_transformer_builder.get_wgs84_bbox()
    wgs84_bbox_polygon = Polygon([
        [bbox[0], bbox[1]],
        [bbox[2], bbox[1]],
        [bbox[2], bbox[3]],
        [bbox[0], bbox[3]],
        [bbox[0], bbox[1]],
    ])

    def cull_geom(geom: BaseGeometry):
        return geom.intersection(wgs84_bbox_polygon)

    wgs84_to_utm_canvas_transformer = utm_projection_transformer_builder\
        .build_wgs84_to_utm_on_canvas()

    # Transform array of polygons to canvas:
    def transform_geom_to_canvas(geom: BaseGeometry):
        return ops.transform(wgs84_to_utm_canvas_transformer, geom)

    def transform_geoms_to_canvas(
        geoms: List[BaseGeometry]
    ) -> List[BaseGeometry]:
        geoms = list(map(cull_geom, geoms))
        # After culling geoms, we might end up with empty objects, so we filter
        # those objects out from the list
        geoms = list(filter(lambda geom: not geom.is_empty, geoms))
        geoms = list(map(transform_geom_to_canvas, geoms))
        return geoms

    land_shapes = transform_geoms_to_canvas(land_shapes)
    lake_shapes = transform_geoms_to_canvas(lake_shapes)

    # Set the black background
    background = Background()
    background.color = (0, 0, 0, 1)
    background.draw(canvas)

    # Render shapes
    polygon_drawer = PolygonDrawer()
    polygon_drawer.fill_color = (1, 1, 1, 1)
    polygon_drawer.geoms = land_shapes
    polygon_drawer.draw(canvas)

    polygon_drawer.fill_color = (0, 0, 0, 1)
    polygon_drawer.geoms = lake_shapes
    polygon_drawer.draw(canvas)

    canvas.close()


if __name__ == '__main__':
    render()
