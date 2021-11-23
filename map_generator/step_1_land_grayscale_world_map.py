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
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

from map_generator.lego_projection_transformer_builder import \
    LegoProjectionTransformerBuilder


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
    "--pixel-scale-factor",
    default=1,
    help='Controls the size of the image'
)
def render(dst: str, aliased: bool, pixel_scale_factor: int):
    # Specify the files to load, and where to save
    data_path = Path(__file__).parent.parent.joinpath('data')
    land_shape_path = data_path.joinpath('ne_110m_land/ne_110m_land.shp')
    lake_shape_path = data_path.joinpath('ne_110m_lakes/ne_110m_lakes.shp')
    canvas_path = Path(dst)
    canvas_path.unlink(missing_ok=True)

    # Create the canvas
    canvas_builder = CanvasBuilder()
    canvas_builder.set_path(canvas_path)
    canvas_width = CanvasUnit.from_px(128)
    canvas_height = CanvasUnit.from_px(80)
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

    lego_projection_transformer_builder = LegoProjectionTransformerBuilder(
        canvas_width,
        canvas_height
    )

    wgs84_to_lego_transformer = lego_projection_transformer_builder.\
        build_wgs84_to_lego()

    def anti_meridian_transformer(x: float, y: float) -> Tuple[float, float]:
        # See `lego_projection_transformer()`
        x_offset = CanvasUnit.from_px(-4)
        if x_offset.pt > 0:
            return (x - canvas_width.pt), y
        else:
            return (x + canvas_width.pt), y

    # Transform array of polygons to canvas:
    def transform_geom_to_canvas(geom: BaseGeometry):
        return ops.transform(wgs84_to_lego_transformer, geom)

    def transform_anti_meridian(geom: BaseGeometry):
        return ops.transform(anti_meridian_transformer, geom)

    def transform_geoms_to_canvas(
        geoms: List[BaseGeometry]
    ) -> List[BaseGeometry]:
        # Because the world wraps along the anti-meridian, we need the exact
        # same polygons shifted by the canvas's width.
        left_geoms = list(map(transform_geom_to_canvas, geoms))
        right_geoms = list(map(transform_anti_meridian, left_geoms))
        return left_geoms + right_geoms

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
