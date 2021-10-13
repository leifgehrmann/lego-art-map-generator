from typing import Tuple, Callable

from map_engraver.canvas.canvas_unit import CanvasUnit


class LegoProjectionTransformerBuilder:

    def __init__(
            self,
            canvas_width: CanvasUnit,
            canvas_height: CanvasUnit
    ):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def build_wgs84_to_lego(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        def wgs84_to_lego_transformer(
                longitude: float,
                latitude: float
        ) -> Tuple[float, float]:
            """
            The Lego projection stretches the map vertically in a non-linear
            way, and also applies a horizontal offset.
            """
            x_percentage = (longitude + 180) / 360
            x_offset = CanvasUnit.from_px(-4)
            x_canvas = x_percentage * self.canvas_width.pt + x_offset.pt

            # The latitude mappings below assume that the canvas height is
            # 80px.
            if latitude < -83:
                min_latitude_range = -90
                max_latitude_range = -83
                # Add 1 to ensure the transformed polygon doesn't
                # self-intersect.
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

        return wgs84_to_lego_transformer
