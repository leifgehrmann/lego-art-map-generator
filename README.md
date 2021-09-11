# lego-art-map-generator

Scripts for generating custom mosaics for the LEGO Art 'World Map' set.

It also has some notes of my research into the original LEGO 'World Map' set,
such as how LEGO might have created the projection, and any interesting design
decisions they made.

**This project is not affiliated with The Lego Group.**

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

The box set contains an excess number of tiles to allow you to customise the
world a bit, but the excess number is not uniform for every color. For example,
you are given 3062 white tiles, and only have 2 unused tile left to spare.

The total number of tiles for each color are listed below:

| Tile color | # of tiles required for World Map | # of tiles in box set according to booklet | Actual # of tiles in my box |
|---|---|---|---|
| ![White](https://img.shields.io/badge/-White-snow) | 3062 | 3064 | 3198 |
| ![Navy](https://img.shields.io/badge/-Navy-rgb(0,53,91)) | 392 | 393 | 410 |
| ![Cyan](https://img.shields.io/badge/-Cyan-rgb(19,183,210)) | 1606 | 1607 | |
| ![Teal](https://img.shields.io/badge/-Teal-rgb(0,153,150)) | 1878 | 1879 | |
| ![Green](https://img.shields.io/badge/-Green-rgb(0,161,55)) | 529 | 601 | 621 |
| ![Olive](https://img.shields.io/badge/-Olive-rgb(162,197,16)) | 1019 | 1060 | 1106 |
| ![Beige](https://img.shields.io/badge/-Beige-rgb(226,202,144)) | 724 | 725 | 752 |
| ![Yellow](https://img.shields.io/badge/-Yellow-rgb(248,172,0)) | 598 | 599 | 619|
| ![Orange](https://img.shields.io/badge/-Orange-rgb(238,117,0)) | 229 | 601 | 625 |
| ![Pink](https://img.shields.io/badge/-Pink-rgb(237,106,112)) | 203 | 601 | |
| **Total** | 10240 | 11130 |

I also collected statistics on individual bags that I found in my set.
Your tile count will probably be different to mine, since there appears to be
some randomness.

| Bag name | tile count |
|---|---|
| White bag 1 | 1065 |
| White bag 2 | 1067 |
| White bag 3 | 1064 |
| White extras bag | 2 |
| Navy bag 1 | 408 |
| Navy extras bag | 2 |
| Cyan bag 1 | 829 |
| Cyan bag 2 |  |
| Cyan extras bag | 2 |
| Teal bag 1 | 977 |
| Teal bag 2 |  |
| Teal extras bag | 2 |
| Green bag | 619 |
| Green extras bag | 2 |
| Olive bag | 1104 |
| Olive extras bag | 2 |
| Beige bag | 750 |
| Beige extras bag | 2 |
| Yellow bag | 617 |
| Yellow extras bag | 2 |
| Orange bag | 623 |
| Orange extras bag | 2 |

## Script descriptions

### count_tiles.py

Iterates through space separated CSV or ASCII Grid files and  returns the total
number of tiles grouped by the tile number.  

How to run:

```console
% poetry run python count_tiles.py ./world-map-tiles/col-*.asc
```
