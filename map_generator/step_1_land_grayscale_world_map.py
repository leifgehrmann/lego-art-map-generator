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
def render(dst: str, aliased: bool):
    # Specify the files to load, and where to save
    data_path = Path(__file__).parent.parent.joinpath('data')
    land_shape_path = data_path.joinpath('ne_110m_land.shp')
    lake_shape_path = data_path.joinpath('ne_110m_lakes.shp')
    canvas_path = Path(dst)
    canvas_path.unlink(missing_ok=True)

    # Create the canvas
    canvas_builder = CanvasBuilder()
    canvas_builder.set_path(canvas_path)
    canvas_width = CanvasUnit.from_px(128)
    canvas_height = CanvasUnit.from_px(80)
    canvas_builder.set_size(canvas_width, canvas_height)
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

    def lego_projection_transformer(
            longitude: float,
            latitude: float
    ) -> Tuple[float, float]:
        """
        The Lego projection stretches the map vertically in a non-linear way,
        and also applies a horizontal offset.
        """
        x_percentage = (longitude + 180) / 360
        x_offset = CanvasUnit.from_px(-4)
        x_canvas = x_percentage * canvas_width.pt + x_offset.pt

        # The latitude mappings below assume that the canvas height is 80px.
        if latitude < -83:
            min_latitude_range = -90
            max_latitude_range = -83
            # Add 1 to ensure the transformed polygon doesn't self-intersect.
            min_y_range = CanvasUnit.from_px(80 + 1).pt
            max_y_range = CanvasUnit.from_px(80).pt
        elif latitude < -60:
            min_latitude_range = -83
            max_latitude_range = -60
            min_y_range = CanvasUnit.from_px(80).pt
            max_y_range = CanvasUnit.from_px(70).pt
        elif latitude < -57:
            min_latitude_range = -60
            max_latitude_range = -57
            min_y_range = CanvasUnit.from_px(70).pt
            max_y_range = CanvasUnit.from_px(67).pt
        elif latitude < 86:
            min_latitude_range = -57
            max_latitude_range = 86
            min_y_range = CanvasUnit.from_px(67).pt
            max_y_range = CanvasUnit.from_px(4).pt
        elif latitude < 86:
            min_latitude_range = 86
            max_latitude_range = 86
            min_y_range = CanvasUnit.from_px(4).pt
            max_y_range = CanvasUnit.from_px(4).pt
        else:
            min_latitude_range = 86
            max_latitude_range = 90
            min_y_range = CanvasUnit.from_px(4).pt
            max_y_range = CanvasUnit.from_px(0).pt

        y_percentage = (latitude - min_latitude_range) / \
                       (max_latitude_range - min_latitude_range)
        y_canvas = y_percentage * (max_y_range - min_y_range) + min_y_range
        return x_canvas, y_canvas

    def anti_meridian_transformer(x: float, y: float) -> Tuple[float, float]:
        # See `lego_projection_transformer()`
        x_offset = CanvasUnit.from_px(-4)
        if x_offset.pt > 0:
            return (x - canvas_width.pt), y
        else:
            return (x + canvas_width.pt), y

    # Transform array of polygons to canvas:
    def transform_geom_to_canvas(geom: BaseGeometry):
        return ops.transform(lego_projection_transformer, geom)

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
