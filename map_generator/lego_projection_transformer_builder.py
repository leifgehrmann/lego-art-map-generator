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
                'canvas_range_start': 80/80 * canvas_height.px + 1,
                'canvas_range_stop': 80/80 * canvas_height.px,
            },
            {
                'latitude_range_start': -83.0,
                'latitude_range_stop': -60.0,
                'canvas_range_start': 80/80 * canvas_height.px,
                'canvas_range_stop': 70/80 * canvas_height.px,
            },
            {
                'latitude_range_start': -60.0,
                'latitude_range_stop': -57.0,
                'canvas_range_start': 70/80 * canvas_height.px,
                'canvas_range_stop': 66.5/80 * canvas_height.px,
            },
            {
                'latitude_range_start': -57.0,
                'latitude_range_stop': 86.0,
                'canvas_range_start': 66.5/80 * canvas_height.px,
                'canvas_range_stop': 3.5/80 * canvas_height.px,
            },
            {
                'latitude_range_start': 86.0,
                'latitude_range_stop': 90.0,
                'canvas_range_start': 3.5/80 * canvas_height.px,
                'canvas_range_stop': 0/80 * canvas_height.px,
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
                    min_y_range = CanvasUnit.from_px(
                        stretch_band['canvas_range_start']
                    ).pt
                    max_y_range = CanvasUnit.from_px(
                        stretch_band['canvas_range_stop']
                    ).pt
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
                x_canvas_px: float,
                y_canvas_px: float
        ) -> Tuple[float, float]:
            x_canvas = CanvasUnit.from_px(x_canvas_px).pt
            y_canvas = CanvasUnit.from_px(y_canvas_px).pt
            x_offset = CanvasUnit.from_px(-4/128 * self.canvas_width.px)
            x_percentage = (x_canvas - x_offset.pt) / self.canvas_width.pt
            longitude = (x_percentage * 360 + 360) % 360 - 180

            min_latitude_range = None
            max_latitude_range = None
            min_y_range = None
            max_y_range = None

            for stretch_band in self.stretch_bands:
                canvas_range_start_in_pt = CanvasUnit.from_px(
                    stretch_band['canvas_range_start']
                ).pt
                canvas_range_stop_in_pt = CanvasUnit.from_px(
                    stretch_band['canvas_range_stop']
                ).pt
                if ((
                        canvas_range_start_in_pt >= y_canvas or
                        isclose(canvas_range_start_in_pt, y_canvas)
                ) and (
                        y_canvas >= canvas_range_stop_in_pt or
                        isclose(canvas_range_stop_in_pt, y_canvas)
                )):
                    min_latitude_range = stretch_band['latitude_range_start']
                    max_latitude_range = stretch_band['latitude_range_stop']
                    min_y_range = canvas_range_start_in_pt
                    max_y_range = canvas_range_stop_in_pt
                    break

            if (
                    min_latitude_range is None or
                    max_latitude_range is None or
                    min_y_range is None or
                    max_y_range is None
            ):
                raise Exception(
                    'Coordinate (%f, %f) could not be projected' %
                    (x_canvas_px, y_canvas_px)
                )

            y_percentage = (y_canvas - min_y_range)
            y_percentage /= (max_y_range - min_y_range)
            latitude = y_percentage
            latitude *= (max_latitude_range - min_latitude_range)
            latitude += min_latitude_range
            return longitude, latitude

        return wgs84_to_lego_transformer
