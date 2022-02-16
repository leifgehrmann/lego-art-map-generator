# lego-art-map-generator

Scripts for generating custom mosaics for the LEGO [31203 World Map] set.

The mosaics aim to imitate the same style as the original 'World Map' set, with
white tiles representing land and coloured tiles representing the bathymetry.

**This project is not affiliated with The Lego Group.**

[31203 World Map]: https://www.lego.com/en-gb/product/world-map-31203

## Examples

Below is a proof of concept that show a recreation of the LEGO World Map using
the scripts in this repository. One can tweak the parameters to get different
results, so this is just an example of what is possible using these scripts.

| Recreation                                                      | Original (By LEGO)                                      |
|-----------------------------------------------------------------|---------------------------------------------------------|
| ![My attempt at the world map](readme_files/full_custom_x3.png) | ![LEGO map with colours](readme_files/full_lego_x3.png) |

The actual purpose of this repository was to create custom maps. Below are some
examples of what's possible. The land and sea-depth images hopefully provide
some context as to how the bathymetric data is used to distribute the coloured
tiles.

| Rendering   | Land                                                                   | Sea-depth                                                                              | Result                                                            |
|-------------|------------------------------------------------------------------------|----------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| World Map   | ![Land rendering of the World Map](readme_files/land_custom_x3.png)    | ![Grayscale sea-depth rendering of the World Map](readme_files/depth_custom_x3.png)    | ![Rendering of the World Map](readme_files/full_custom_x3.png)    |
| North Sea   | ![Land rendering of the North Sea](readme_files/land_north_sea_x3.png) | ![Grayscale sea-depth rendering of the North Sea](readme_files/depth_north_sea_x3.png) | ![Rendering of the North Sea](readme_files/full_north_sea_x3.png) |
| Iceland     | ![Land rendering of Iceland](readme_files/land_iceland_x3.png)         | ![Grayscale sea-depth rendering of Iceland](readme_files/depth_iceland_x3.png)         | ![Rendering of Iceland](readme_files/full_iceland_x3.png)         |
| Denmark     | ![Land rendering of Denmark](readme_files/land_denmark_x3.png)         | ![Grayscale sea-depth rendering of Denmark](readme_files/depth_denmark_x3.png)         | ![Rendering of Denmark](readme_files/full_denmark_x3.png)         |
| Greece      | ![Land rendering of Greece](readme_files/land_greece_x3.png)           | ![Grayscale sea-depth rendering of Greece](readme_files/depth_greece_x3.png)           | ![Rendering of Greece](readme_files/full_greece_x3.png)           |
| Madagascar  | ![Land rendering of Madagascar](readme_files/land_madagascar_x3.png)   | ![Grayscale sea-depth rendering of Madagascar](readme_files/depth_madagascar_x3.png)   | ![Rendering of Madagascar](readme_files/full_madagascar_x3.png)   |
| New Guinea  | ![Land rendering of New Guinea](readme_files/land_new_guinea_x3.png)   | ![Grayscale sea-depth rendering of New Guinea](readme_files/depth_new_guinea_x3.png)   | ![Rendering of New Guinea](readme_files/full_new_guinea_x3.png)   |
| Corsica     | ![Land rendering of Corsica](readme_files/land_corsica_x3.png)         | ![Grayscale sea-depth rendering of Corsica](readme_files/depth_corsica_x3.png)         | ![Rendering of Corsica](readme_files/full_corsica_x3.png)         |
| New Zealand | ![Land rendering of New Zealand](readme_files/land_new_zealand_x3.png) | ![Grayscale sea-depth rendering of New Zealand](readme_files/depth_new_zealand_x3.png) | ![Rendering of New Zealand](readme_files/full_new_zealand_x3.png) |

## Project structure

The project is grouped in three sections:

* [`data`](/data) - Where all the raster and shapefile data is stored, such as bathymetry and coastline data.
* [`map_generator`](/map_generator) - Scripts to generate the mosaics
* [`map_analysis`](/map_analysis) - Scripts to analyse tile distributions and bathymetric data.

### Pre-requisites

First make sure python is installed. Then run the following commands to install
dependencies and download map data.

```commandline
make install
make download_ne_data
make download_gebco_data
```

## Map Generation

Map generation is split into 5 steps, each is its own script:

* Step 1: Generate a grayscale image of the land-masses.
* Step 2: Convert the image in step 1 into a 1-bit image.
* Step 3: Modify the image in step 2 by adding a shadow to the edges of each landmass. 
* Step 4: Generate a grayscale bathymetric map.
* Step 5: Use the images in step 3 and 4, to distribute the coloured tiles according to proportions outlined in a CSV.

| Step 1                                               | Step 2                                               | Step 3                                               | Step 4                                               | Step 5                                               |
|------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|------------------------------------------------------|
| ![LEGO map with colours](readme_files/step_1_x3.png) | ![LEGO map with colours](readme_files/step_2_x3.png) | ![LEGO map with colours](readme_files/step_3_x3.png) | ![LEGO map with colours](readme_files/step_4_x3.png) | ![LEGO map with colours](readme_files/step_5_x3.png) |

### Step 1 - Coastline generation

This step comes in two varieties.

To recreate the world map similar to the LEGO world map, you'll run this script:

```commandline
poetry run python map_generator/step_1_land_grayscale_world_map.py step_1.png
```

To generate a custom map of a specific part of the globe, you'll run this other
script, which takes in numerous parameters for controlling the projection. This
includes `center` (longitude/latitude), `scale` (meters per pixel), `rotation`
(Degrees). The UTM projection is used, and will adapt to the `center` position
you pick to minimize distortion. You can also control the size of the canvas
using `size`.

```commandline
poetry run python map_generator/step_1_land_grayscale_utm_map.py step_1.png --size=80,128 --center=1.8,58.8 --scale=15000 --rotation=25
```

Here is an example of the output:

![Map using a threshold filter](readme_files/land_grayscale_x3.png)

### Step 2 - Converting the image to a 1-bit image

This script will convert a grayscale image of the landmasses into a 1-bit image
consisting only of black and white pixels. The algorithm used can be controlled
with the `mode` flag.

```commandline
poetry run python map_generator/step_2_grayscale_to_1bit.py step_1.png step_2.png --mode=custom_1
```

The different modes are: 

* `threshold` uses a simple 50/50 [Threshold Filter],
* `dither` uses [Floyd-Steinberg Dithering],
* `custom_1` uses a custom algorithm I made that does some vague kernel
filtering that takes into account the neighboring pixels. This mode is
recommended because the other modes often lose detail or add
unwanted details.

| `threshold`                                                         | `dither`                                                         | `custom_1`                                                     |
|---------------------------------------------------------------------|------------------------------------------------------------------|----------------------------------------------------------------|
| ![Map using a threshold filter](readme_files/land_threshold_x3.png) | ![Map using a dithering filter](readme_files/land_dither_x3.png) | ![Map using Pillow's convert](readme_files/land_custom_x3.png) |

[Threshold Filter]: https://en.wikipedia.org/wiki/Thresholding_(image_processing)
[Floyd-Steinberg Dithering]: https://en.wikipedia.org/wiki/Floyd–Steinberg_dithering

### Step 3 - Add a shadow to the landmasses

This script takes any black and white image from step 2 (`step_2.png`), adds a
dark-blue  shadow to the white tiles on the right-hand side, and saves it to an
output path (`step_3.png`)

```commandline
poetry run python map_generator/step_3_land_shadow.py step_2.png step_3.png
```

### Step 4

### Step 5

### Step 6 - Generate High-res image (Optional)

Optionally, if you want to create an enlarged scale of the final image with
rounded tiles instead of pixels, you can run this script.

```commandline
poetry run python map_generator/step_6_pixels_to_lego.py step_5.png step_6.png
```

-----

## Map Analysis

### count_tiles_from_ascii.py and count_tiles_from_image.py

When I started this project, I created a bunch of ASCII Grid files that
represented the tile placements in the LEGO World Map. You can see them in
[/data/lego_world_map_ascii/](/data/lego_world_map_ascii/).

I created a script that counts the unique numbers in the files.

```commandline
poetry run python map_analysis/count_tiles_from_ascii.py data/lego_world_map_ascii/*
``` 

I made a similar script for counting unique colours in an image.

```commandline
poetry run python map_analysis/count_tiles_from_image.py readme_files/full_lego.png
```

## Tile counts

The official box set contains an excess number of tiles to allow you to
customise the world a bit, but the there are different amounts for each color.

The total number of tiles for each color are listed below:

| Tile color | # of tiles required for World Map | # of tiles in box set according to booklet | Actual # of tiles in my box |
|----------------------------------------------------------------|------|------|------|
| ![White](https://img.shields.io/badge/-White-rgb(255,255,255)) | 3062 | 3064 | 3198 |
| ![Navy](https://img.shields.io/badge/-Navy-rgb(0,53,91))       |  392 |  393 |  410 |
| ![Cyan](https://img.shields.io/badge/-Cyan-rgb(19,183,210))    | 1606 | 1607 | 1668 |
| ![Teal](https://img.shields.io/badge/-Teal-rgb(0,153,150))     | 1878 | 1879 | 1956 |
| ![Green](https://img.shields.io/badge/-Green-rgb(0,161,55))    |  529 |  601 |  621 |
| ![Olive](https://img.shields.io/badge/-Olive-rgb(162,197,16))  | 1019 | 1060 | 1106 |
| ![Beige](https://img.shields.io/badge/-Beige-rgb(226,202,144)) |  724 |  725 |  752 |
| ![Yellow](https://img.shields.io/badge/-Yellow-rgb(248,172,0)) |  598 |  599 |  619 |
| ![Orange](https://img.shields.io/badge/-Orange-rgb(238,117,0)) |  229 |  601 |  625 |
| ![Coral](https://img.shields.io/badge/-Coral-rgb(237,106,112)) |  203 |  601 |  627 |
| **Total** | **10240** | **11130** | **11582** |

I also collected statistics on individual bags that I found in my set.
Your tile count will probably be different to mine, since there appears to be
some randomness.

| Bag name          | tile count |
|-------------------|------------|
| White bag 1       | 1065       |
| White bag 2       | 1067       |
| White bag 3       | 1064       |
| White extras bag  | 2          |
| Navy bag 1        | 408        |
| Navy extras bag   | 2          |
| Cyan bag 1        | 829        |
| Cyan bag 2        | 837        |
| Cyan extras bag   | 2          |
| Teal bag 1        | 977        |
| Teal bag 2        | 977        |
| Teal extras bag   | 2          |
| Green bag         | 619        |
| Green extras bag  | 2          |
| Olive bag         | 1104       |
| Olive extras bag  | 2          |
| Beige bag         | 750        |
| Beige extras bag  | 2          |
| Yellow bag        | 617        |
| Yellow extras bag | 2          |
| Orange bag        | 623        |
| Orange extras bag | 2          |
| Coral bag         | 625        |
| Coral extras bag  | 2          |

## Script descriptions

### count_tiles_from_ascii.py

Iterates through space separated CSV or ASCII Grid files and returns the total
number of tiles grouped by the tile number.  

How to run:

```console
% poetry run python map_analysis/count_tiles_from_ascii.py ./data/lego_world_map_ascii/column-*.asc
```

### count_tiles_from_image.py

Iterates through image files and returns the total number of tiles grouped by
the tile color.  

How to run:

```console
% poetry run python map_analysis/count_tiles_from_image.py ./readme_files/full_lego.png
```
