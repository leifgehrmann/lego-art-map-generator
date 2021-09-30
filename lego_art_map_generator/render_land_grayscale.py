from pathlib import Path
from typing import List

import pyproj
import shapefile
from map_engraver.canvas import CanvasBuilder

from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data import geo_canvas_ops
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from map_engraver.drawable.layout.background import Background
from shapely import ops
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

# Map projection configurations:
# Stretch the world map height
y_scale = 1.25
# Shift the world map in pixels
x_offset = CanvasUnit.from_px(-4)
y_offset = CanvasUnit.from_px(1)

# Specify the files to load, and where to save
data_path = Path(__file__).parent.parent.joinpath('data')
land_shape_path = data_path.joinpath('ne_110m_land.shp')
lake_shape_path = data_path.joinpath('ne_110m_lakes.shp')
output_path = Path(__file__).parent.parent.joinpath('output')
output_path.mkdir(parents=True, exist_ok=True)
canvas_path = output_path.joinpath('land_grayscale.png')
canvas_path.unlink(missing_ok=True)

# Create the canvas
canvas_builder = CanvasBuilder()
canvas_builder.set_path(canvas_path)
canvas_width = CanvasUnit.from_px(128)
canvas_height = CanvasUnit.from_px(80)
canvas_builder.set_size(canvas_width, canvas_height)
canvas = canvas_builder.build()


# Read world map shapefile
def parse_shapefile(shapefile_path: Path):
    shapefile_collection = shapefile.Reader(shapefile_path.as_posix())
    shapely_objects = []
    for shape_record in shapefile_collection.shapeRecords():
        shapely_objects.append(shape(shape_record.shape.__geo_interface__))
    return shapely_objects


land_shapes = parse_shapefile(land_shape_path)
lake_shapes = parse_shapefile(lake_shape_path)


# Invert CRS for shapes, because shapefiles are store coordinates are lon/lat,
# not according to the ISO-approved standard.
def transform_geoms_to_invert(geoms: List[BaseGeometry]):
    return list(map(
        lambda geom: ops.transform(lambda x, y: (y, x), geom),
        geoms
    ))


wgs84_crs = pyproj.CRS.from_epsg(4326)
geo_canvas_scale = geo_canvas_ops.GeoCanvasScale(360, canvas_width)
origin_for_geo = GeoCoordinate(-180, 90, wgs84_crs)
wgs84_canvas_transformer_raw = geo_canvas_ops.build_transformer(
    crs=wgs84_crs,
    scale=geo_canvas_scale,
    origin_for_geo=origin_for_geo
)


def wgs84_canvas_transformer(x, y):
    coord = wgs84_canvas_transformer_raw(x, y)
    return (coord[0] + x_offset.pt), (coord[1] + y_offset.pt) * y_scale


def anti_meridian_transformer(x, y):
    if x_offset.pt > 0:
        return (x - canvas_width.pt), y
    else:
        return (x + canvas_width.pt), y


# Transform array of polygons to canvas:
def transform_geom_to_canvas(geom: BaseGeometry):
    return ops.transform(wgs84_canvas_transformer, geom)


def transform_anti_meridian(geom: BaseGeometry):
    return ops.transform(anti_meridian_transformer, geom)


def transform_geoms_to_canvas(geoms: List[BaseGeometry]) -> List[BaseGeometry]:
    # Because the world wraps along the anti-meridian, we need the exact same
    # polygons shifted by the canvas's width.
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
