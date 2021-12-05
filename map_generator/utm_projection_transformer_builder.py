import math
from typing import Tuple, Callable

from map_engraver.canvas.canvas_unit import CanvasUnit
from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


class UtmProjectionTransformerBuilder:

    def __init__(
            self,
            canvas_width: CanvasUnit,
            canvas_height: CanvasUnit,
            center_longitude: float,
            center_latitude: float,
            scale: float,
            rotation: float
    ):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.center_longitude = center_longitude
        self.center_latitude = center_latitude
        self.scale = scale
        self.rotation = rotation

    def get_utm_proj(self) -> CRS:
        utm_crs_list = query_utm_crs_info(
            datum_name="WGS 84",
            area_of_interest=AreaOfInterest(
                west_lon_degree=self.center_longitude,
                south_lat_degree=self.center_latitude,
                east_lon_degree=self.center_longitude,
                north_lat_degree=self.center_latitude,
            ),
        )
        return CRS.from_epsg(utm_crs_list[0].code)

    def get_wgs84_bbox(self) -> Tuple[float, float, float, float]:
        transformer = self.build_utm_on_canvas_to_wgs84()
        pos_tl = transformer(0, 0)
        pos_tr = transformer(self.canvas_width.px, 0)
        pos_bl = transformer(0, self.canvas_height.px)
        pos_br = transformer(self.canvas_width.px, self.canvas_height.px)
        min_lon = min(pos_tl[0], pos_tr[0], pos_bl[0], pos_br[0])
        max_lon = max(pos_tl[0], pos_tr[0], pos_bl[0], pos_br[0])
        min_lat = min(pos_tl[1], pos_tr[1], pos_bl[1], pos_br[1])
        max_lat = max(pos_tl[1], pos_tr[1], pos_bl[1], pos_br[1])
        return min_lon, min_lat, max_lon, max_lat

    def build_wgs84_to_utm_on_canvas(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        pyproj_transformer = Transformer.from_proj(
            CRS.from_epsg(4326),
            self.get_utm_proj()
        )
        center_x, center_y = pyproj_transformer.transform(
            self.center_latitude,
            self.center_longitude
        )
        rotation_rad = self.rotation / 180 * math.pi

        def transformer(
                longitude: float,
                latitude: float
        ) -> Tuple[float, float]:
            x, y = pyproj_transformer.transform(latitude, longitude)

            # Origin
            x -= center_x
            y -= center_y

            # Scale
            x /= self.scale
            y /= -self.scale

            # Rotate
            x_rot = x * math.cos(rotation_rad) - y * math.sin(rotation_rad)
            y_rot = x * math.sin(rotation_rad) + y * math.cos(rotation_rad)

            # Translate
            return (
                    x_rot + self.canvas_width.pt / 2,
                    y_rot + self.canvas_height.pt / 2
            )

        return transformer

    def build_utm_on_canvas_to_wgs84(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        pyproj_transformer_inv = Transformer.from_proj(
            self.get_utm_proj(),
            CRS.from_epsg(4326)
        )
        pyproj_transformer = Transformer.from_proj(
            CRS.from_epsg(4326),
            self.get_utm_proj()
        )
        center_x, center_y = pyproj_transformer.transform(
            self.center_latitude,
            self.center_longitude
        )
        rotation_rad = self.rotation / 180 * math.pi

        def transformer(
                x_canvas_px: float,
                y_canvas_px: float
        ) -> Tuple[float, float]:
            # Undo translation
            x_rot = x_canvas_px - self.canvas_width.px / 2
            y_rot = y_canvas_px - self.canvas_height.px / 2
            # Undo rotation
            x = x_rot * math.cos(-rotation_rad) - y_rot * math.sin(-rotation_rad)
            y = x_rot * math.sin(-rotation_rad) + y_rot * math.cos(-rotation_rad)
            # Undo scale
            x *= self.scale
            y *= -self.scale
            # Undo origin
            x += center_x
            y += center_y

            latitude, longitude = pyproj_transformer_inv.transform(x, y)

            return longitude, latitude

        return transformer
