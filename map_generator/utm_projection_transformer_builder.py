from typing import Tuple, Callable


class UtmProjectionTransformerBuilder:

    def __init__(
            self,
            canvas_width: int,
            canvas_height: int,
            center_longitude: float,
            center_latitude: float,
            scale: float,
            rotation: float
    ):
        pass

    def build_wgs84_to_utm_on_canvas(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        def transformer(
                longitude: float,
                latitude: float
        ) -> Tuple[float, float]:
            return longitude, latitude

        return transformer

    def build_utm_on_canvas_to_wgs84(
            self
    ) -> Callable[[float, float], Tuple[float, float]]:
        def transformer(
                x_canvas_px: float,
                y_canvas_px: float
        ) -> Tuple[float, float]:
            return x_canvas_px, y_canvas_px

        return transformer
