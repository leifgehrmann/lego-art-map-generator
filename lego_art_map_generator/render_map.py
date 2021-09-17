from pathlib import Path

from map_engraver.canvas import CanvasBuilder

# Create the canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.layout.background import Background

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

# 2. Read world map shapefile
# 3. Transform shapes
# 4. Render land, shifted by 1 pixel
# 5. Render land

canvas.close()
