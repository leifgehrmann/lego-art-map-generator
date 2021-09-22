from pathlib import Path
from typing import List

import cairocffi
import pyproj
import shapefile
from map_engraver.canvas import CanvasBuilder

# Create the canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data import geo_canvas_ops, osm_shapely_ops
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.osm_shapely.osm_point import OsmPoint
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from map_engraver.drawable.layout.background import Background
from shapely import ops
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

output_path = Path(__file__).parent.parent.joinpath('output')
output_path.mkdir(parents=True, exist_ok=True)
path = output_path.joinpath('map-plate-carree.png')
path.unlink(missing_ok=True)
canvas_builder = CanvasBuilder()
canvas_builder.set_path(path)
canvas_builder.set_size(CanvasUnit.from_px(128), CanvasUnit.from_px(80))
canvas = canvas_builder.build()

# Set the black background
background = Background()
background.color = (0, 0, 0, 1)
background.draw(canvas)


# Read world map shapefile
def parse_shapefile(shapefile_path: Path):
    shapefile_collection = shapefile.Reader(shapefile_path.as_posix())
    shapely_objects = []
    for shape_record in shapefile_collection.shapeRecords():
        shapely_objects.append(shape(shape_record.shape.__geo_interface__))
    return shapely_objects


land_shapes = parse_shapefile(Path(__file__).parent.parent.joinpath('data/ne_110m_land.shp'))


# Invert CRS for shapes, because shapefiles are store coordinates are lon/lat,
# not according to the ISO-approved standard.
def transform_geoms_to_invert(geoms: List[BaseGeometry]):
    return list(map(
        lambda geom: ops.transform(lambda x, y: (y, x), geom),
        geoms
    ))


land_shapes = transform_geoms_to_invert(land_shapes)

wgs84_crs = pyproj.CRS.from_epsg(4326)
plate_crs = pyproj.CRS.from_epsg(32662)
plate_crs = pyproj.CRS.from_proj4('+proj=eqc +lat_ts=0 +lat_0=3.5 +lon_0=11.5 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs')
geo_width = 20026376.39 * 2
canvas_width = CanvasUnit.from_px(128)
geo_canvas_scale = geo_canvas_ops.GeoCanvasScale(geo_width, canvas_width)
origin_for_geo = GeoCoordinate(-20026376.39, 9462156.72, plate_crs)
wgs84_canvas_transformer_raw = geo_canvas_ops.build_transformer(
    crs=plate_crs,
    scale=geo_canvas_scale,
    origin_for_geo=origin_for_geo,
    data_crs=wgs84_crs
)


def wgs84_canvas_transformer(x, y):
    coord = wgs84_canvas_transformer_raw(x, y)
    return coord[0], coord[1] * 1


# Transform array of polygons to canvas:
def transform_geom_to_canvas(geom: BaseGeometry):
    if isinstance(geom, OsmPoint):
        return osm_shapely_ops.transform(wgs84_canvas_transformer, geom)
    else:
        return ops.transform(wgs84_canvas_transformer, geom)


def transform_geoms_to_canvas(geoms: List[BaseGeometry]) -> List[BaseGeometry]:
    return list(map(transform_geom_to_canvas, geoms))


# canvas.context.set_antialias(cairocffi.ANTIALIAS_NONE)

land_shapes = transform_geoms_to_canvas(land_shapes)


# Render land, shifted by 1 pixel
def transform_geom_by_1_pixel(geom: BaseGeometry):
    return ops.transform(lambda x, y: (x + 0.5, y), geom)


def transform_geoms_by_1_pixel(geoms: List[BaseGeometry]) -> List[BaseGeometry]:
    return list(map(transform_geom_by_1_pixel, geoms))


# land_shapes_shadow = transform_geoms_by_1_pixel(land_shapes)
#
# land_shadow_drawer = PolygonDrawer()
# land_shadow_drawer.geoms = land_shapes_shadow
#
# land_shadow_drawer.fill_color = (0, 53 / 255, 91 / 255, 1)
# land_shadow_drawer.draw(canvas)

# Render land
land_drawer = PolygonDrawer()
land_drawer.geoms = land_shapes

land_drawer.fill_color = (1, 1, 1, 1)
land_drawer.draw(canvas)

canvas.close()
