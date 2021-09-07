# lego-art-map-generator

Scripts for generating custom mosaics for the LEGO Art 'World Map' set.

This project is not affiliated with The Lego Group.

## Interesting notes about the LEGO Art world map set

* The map appears to be a vertically stretched WGS84/EPSG:4326 projection,
  except all the continents are shifted 11.5 degrees to the west and 3.5 degrees
  to the south. This was probably done to ensure the
  [Chukchi Peninsula][chukchi-peninsula] wasn't cut off.
* Antarctica was also shifted a fair amount, although it's not clear what
  additional transformations were made.
* Unsurprisingly a lot of creative liberties were made with the coastline,
  mostly to emphasize certain islands and coastlines.

![LEGO World Map with coastlines on top](world-map-with-coastlines.png)

[chukchi-peninsula]: https://en.wikipedia.org/wiki/Chukchi_Peninsula
