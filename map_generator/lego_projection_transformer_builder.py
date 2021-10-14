from math import isclose

from typing import Tuple, Callable, TypedDict, List

from map_engraver.canvas.canvas_unit import CanvasUnit


class StretchRange(TypedDict):
    latitude_range_start: float
    latitude_range_stop: float
    canvas_range_start: float
    canvas_range_stop: float


class LegoProjectionTransformerBuilder:
    stretch_bands: List[StretchRange]

    def __init__(
            self,
            canvas_width: CanvasUnit,
            canvas_height: CanvasUnit
    ):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.stretch_bands = [
            {
                'latitude_range_start': -90.0,
                'latitude_range_stop': -83.0,
                'canvas_range_start': CanvasUnit.from_px(80 + 1).pt,
                'canvas_range_stop': CanvasUnit.from_px(80).pt,
            },
            {
                'latitude_range_start': -83.0,
                'latitude_range_stop': -60.0,
                'canvas_range_start': CanvasUnit.from_px(80).pt,
                'canvas_range_stop': CanvasUnit.from_px(70).pt,
            },
            {
                'latitude_range_start': -60.0,
                'latitude_range_stop': -57.0,
                'canvas_range_start': CanvasUnit.from_px(70).pt,
                'canvas_range_stop': CanvasUnit.from_px(67).pt,
            },
            {
                'latitude_range_start': -57.0,
                'latitude_range_stop': 86.0,
                'canvas_range_start': CanvasUnit.from_px(67).pt,
                'canvas_range_stop': CanvasUnit.from_px(4).pt,
            },
            {
                'latitude_range_start': 86.0,
                'latitude_range_stop': 90.0,
                'canvas_range_start': CanvasUnit.from_px(4).pt,
                'canvas_range_stop': CanvasUnit.from_px(0).pt,
            }
        ]

    def build_wgs84_to_lego(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        def wgs84_to_lego_transformer(
                longitude: float,
                latitude: float
        ) -> Tuple[float, float]:
            x_percentage = (longitude + 180) / 360
            x_offset = CanvasUnit.from_px(-4)
            x_canvas = x_percentage * self.canvas_width.pt + x_offset.pt

            min_latitude_range = None
            max_latitude_range = None
            min_y_range = None
            max_y_range = None

            # The latitude mappings below assume that the canvas height is
            # 80px.
            for stretch_band in self.stretch_bands:
                if ((
                        stretch_band['latitude_range_start'] <= latitude or
                        isclose(stretch_band['latitude_range_start'], latitude)
                ) and
                        latitude < stretch_band['latitude_range_stop']
                ):
                    min_latitude_range = stretch_band['latitude_range_start']
                    max_latitude_range = stretch_band['latitude_range_stop']
                    min_y_range = stretch_band['canvas_range_start']
                    max_y_range = stretch_band['canvas_range_stop']
                    break

            if (
                    min_latitude_range is None or
                    max_latitude_range is None or
                    min_y_range is None or
                    max_y_range is None
            ):
                raise Exception(
                    'Coordinate (%f, %f) could not be projected' %
                    (longitude, latitude)
                )

            y_percentage = (latitude - min_latitude_range) / \
                           (max_latitude_range - min_latitude_range)
            y_canvas = y_percentage * (max_y_range - min_y_range) + min_y_range
            return x_canvas, y_canvas

        return wgs84_to_lego_transformer

    def build_lego_to_wgs84(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        def wgs84_to_lego_transformer(
                x_canvas: float,
                y_canvas: float
        ) -> Tuple[float, float]:
            x_offset = CanvasUnit.from_px(-4)
            x_percentage = (x_canvas - x_offset.pt) / self.canvas_width.pt
            longitude = (x_percentage * 360 + 180) % 360 - 180

            min_latitude_range = None
            max_latitude_range = None
            min_y_range = None
            max_y_range = None

            # The latitude mappings below assume that the canvas height is
            # 80px.
            for stretch_band in self.stretch_bands:
                if ((
                        stretch_band['canvas_range_start'] <= y_canvas or
                        isclose(stretch_band['canvas_range_start'], y_canvas)
                ) and
                        y_canvas < stretch_band['canvas_range_stop']
                ):
                    min_latitude_range = stretch_band['latitude_range_start']
                    max_latitude_range = stretch_band['latitude_range_stop']
                    min_y_range = stretch_band['canvas_range_start']
                    max_y_range = stretch_band['canvas_range_stop']
                    break

            if (
                    min_latitude_range is None or
                    max_latitude_range is None or
                    min_y_range is None or
                    max_y_range is None
            ):
                raise Exception(
                    'Coordinate (%f, %f) could not be projected' %
                    (x_canvas, y_canvas)
                )

            y_percentage = (y_canvas - min_y_range) / (max_y_range - min_y_range)
            latitude = y_percentage * (max_latitude_range - min_latitude_range) + min_latitude_range
            return longitude, latitude

        return wgs84_to_lego_transformer
