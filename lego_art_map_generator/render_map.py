from pathlib import Path
from typing import List

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
from shapely.geometry import shape, Polygon
from shapely.geometry.base import BaseGeometry

output_path = Path(__file__).parent.parent.joinpath('output')
output_path.mkdir(parents=True, exist_ok=True)
path = output_path.joinpath('map.png')
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


land_shapes = parse_shapefile(
    Path(__file__).parent.parent.joinpath('data/ne_110m_land.shp')
)

lake_shapes = parse_shapefile(
    Path(__file__).parent.parent.joinpath('data/ne_110m_lakes.shp')
)


# Subtract lakes from land
def subtract_lakes_from_land(land: Polygon, lakes: List[Polygon]):
    for lake in lakes:
        try:
            land = land.difference(lake)
        except TopologyException:
            pass

    return land


land_shapes = list(map(
    lambda geom: subtract_lakes_from_land(geom, lake_shapes),
    land_shapes
))


# Invert CRS for shapes, because shapefiles are store coordinates are lon/lat,
# not according to the ISO-approved standard.
def transform_geoms_to_invert(geoms: List[BaseGeometry]):
    return list(map(
        lambda geom: ops.transform(lambda x, y: (y, x), geom),
        geoms
    ))


wgs84_crs = pyproj.CRS.from_epsg(4326)
canvas_width = CanvasUnit.from_px(128)
geo_canvas_scale = geo_canvas_ops.GeoCanvasScale(360, canvas_width)
origin_for_geo = GeoCoordinate(-180, 90, wgs84_crs)
wgs84_canvas_transformer_raw = geo_canvas_ops.build_transformer(
    crs=wgs84_crs,
    scale=geo_canvas_scale,
    origin_for_geo=origin_for_geo
)


def wgs84_canvas_transformer(x, y):
    coord = wgs84_canvas_transformer_raw(x, y)
    y_scale = 1.25
    x_offset = -3
    y_offset = 1
    return (coord[0] + x_offset), (coord[1] + y_offset) * y_scale


# Transform array of polygons to canvas:
def transform_geom_to_canvas(geom: BaseGeometry):
    if isinstance(geom, OsmPoint):
        return osm_shapely_ops.transform(wgs84_canvas_transformer, geom)
    else:
        return ops.transform(wgs84_canvas_transformer, geom)


def transform_geoms_to_canvas(geoms: List[BaseGeometry]) -> List[BaseGeometry]:
    return list(map(transform_geom_to_canvas, geoms))


land_shapes = transform_geoms_to_canvas(land_shapes)

# Render land
land_drawer = PolygonDrawer()
land_drawer.geoms = land_shapes

land_drawer.fill_color = (1, 1, 1, 1)
land_drawer.draw(canvas)

canvas.close()
