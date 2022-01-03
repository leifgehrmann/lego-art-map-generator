.PHONY: help readme_files
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

install: ## install dependencies
	poetry install

download_ne_data: ## Download data from natural earth
	curl -o data/ne_110m_land.zip https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip
	unzip -o -d data/ne_110m_land data/ne_110m_land.zip
	curl -o data/ne_110m_lakes.zip https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_lakes.zip
	unzip -o -d data/ne_110m_lakes data/ne_110m_lakes.zip
	curl -o data/ne_10m_land.zip https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_land.zip
	unzip -o -d data/ne_10m_land data/ne_10m_land.zip
	curl -o data/ne_10m_lakes.zip https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_lakes.zip
	unzip -o -d data/ne_10m_lakes data/ne_10m_lakes.zip

download_gebco_data: ## Download data from gebco.net
	curl -o data/gebco_2021_sub_ice_topo_geotiff.zip https://www.bodc.ac.uk/data/open_download/gebco/gebco_2021_sub_ice_topo/geotiff/
	unzip -o -d data/gebco_2021_sub_ice_topo_geotiff data/gebco_2021_sub_ice_topo_geotiff.zip

readme_files:
	poetry run python map_generator/step_1_land_grayscale_world_map.py readme_files/land_grayscale.png
	poetry run python map_generator/step_1_land_grayscale_world_map.py readme_files/land_aliased.png --aliased
	poetry run python map_generator/step_2_grayscale_to_1bit.py readme_files/land_grayscale.png readme_files/land_threshold.png --mode=threshold
	poetry run python map_generator/step_2_grayscale_to_1bit.py readme_files/land_grayscale.png readme_files/land_dither.png --mode=dither
	poetry run python map_generator/step_2_grayscale_to_1bit.py readme_files/land_grayscale.png readme_files/land_custom.png --mode=custom_1
	convert readme_files/full_lego.png -filter box -resize 384x240 readme_files/full_lego_x3.png
	convert readme_files/land_aliased.png -filter box -resize 384x240 readme_files/land_aliased_x3.png
	convert readme_files/land_dither.png -filter box -resize 384x240 readme_files/land_dither_x3.png
	convert readme_files/land_grayscale.png -filter box -resize 384x240 readme_files/land_grayscale_x3.png
	convert readme_files/land_lego.png -filter box -resize 384x240 readme_files/land_lego_x3.png
	convert readme_files/land_threshold.png -filter box -resize 384x240 readme_files/land_threshold_x3.png
	convert readme_files/land_custom.png -filter box -resize 384x240 readme_files/land_custom_x3.png
	convert output/world_map_step_4.png -filter box -resize 384x240 readme_files/depth_custom_x3.png
	convert output/world_map_step_5.png -filter box -resize 384x240 readme_files/full_custom_x3.png
	convert output/north_sea_step_2.png -filter box -resize 240x384 readme_files/land_north_sea_x3.png
	convert output/north_sea_step_4.png -filter box -resize 240x384 readme_files/depth_north_sea_x3.png
	convert output/north_sea_step_5.png -filter box -resize 240x384 readme_files/full_north_sea_x3.png
	convert output/iceland_step_2.png -filter box -resize 384x240 readme_files/land_iceland_x3.png
	convert output/iceland_step_4.png -filter box -resize 384x240 readme_files/depth_iceland_x3.png
	convert output/iceland_step_5.png -filter box -resize 384x240 readme_files/full_iceland_x3.png
	convert output/greece_step_2.png -filter box -resize 384x240 readme_files/land_greece_x3.png
	convert output/greece_step_4.png -filter box -resize 384x240 readme_files/depth_greece_x3.png
	convert output/greece_step_5.png -filter box -resize 384x240 readme_files/full_greece_x3.png

world_map_example:
	poetry run python map_generator/step_1_land_grayscale_world_map.py output/world_map_step_1.png
	poetry run python map_generator/step_2_grayscale_to_1bit.py output/world_map_step_1.png output/world_map_step_2.png --mode=custom_1
	poetry run python map_generator/step_3_land_shadow.py output/world_map_step_2.png output/world_map_step_3.png
	poetry run python map_generator/step_4_sea_grayscale_world_map.py output/world_map_step_3.png output/world_map_step_4.png
	poetry run python map_generator/step_5_sea_2.py output/world_map_step_3.png output/world_map_step_4.png data/world_map_brightness_tile_proportion_2.csv data/world_map_max_tile_counts.csv output/world_map_step_5.png

north_sea_example:
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/north_sea_step_1_x4.png --size=80,128 --center=1.8,58.8 --scale=15000 --rotation=25 --pixel-scale-factor=4
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/north_sea_step_1.png --size=80,128 --center=1.8,58.8 --scale=15000 --rotation=25
	poetry run python map_generator/step_2_grayscale_to_1bit.py output/north_sea_step_1.png output/north_sea_step_2.png --mode=custom_1
	poetry run python map_generator/step_3_land_shadow.py output/north_sea_step_2.png output/north_sea_step_3.png
	poetry run python map_generator/step_4_sea_grayscale_utm_map.py output/north_sea_step_3.png output/north_sea_step_4.png --size=80,128 --center=1.8,58.8 --scale=15000 --rotation=25 --max-depth=3500
	poetry run python map_generator/step_5_sea_2.py output/north_sea_step_3.png output/north_sea_step_4.png data/north_sea_map_brightness_tile_proportion.csv data/world_map_max_tile_counts.csv output/north_sea_step_5.png

new_zealand_example:
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/new_zealand_step_1_x4.png --size=128,80 --center=-18,65 --scale=5000 --rotation=0 --pixel-scale-factor=4
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/new_zealand_step_1.png --size=80,128 --center=172.8,-41 --scale=11500 --rotation=-15
	poetry run python map_generator/step_2_grayscale_to_1bit.py output/new_zealand_step_1.png output/new_zealand_step_2.png --mode=custom_1
	poetry run python map_generator/step_3_land_shadow.py output/new_zealand_step_2.png output/new_zealand_step_3.png
	# poetry run python map_generator/step_4_sea_grayscale_utm_map.py output/new_zealand_step_3.png output/new_zealand_step_4.png --size=80,128 --center=173,-41 --scale=15000 --rotation=0 --max-depth=3500
	# poetry run python map_generator/step_5_sea_2.py output/new_zealand_step_3.png output/new_zealand_step_4.png data/north_sea_map_brightness_tile_proportion.csv data/world_map_max_tile_counts.csv output/new_zealand_step_5.png

iceland_example:
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/iceland_step_1_x4.png --size=128,80 --center=-18.7,65 --scale=5800 --rotation=0 --pixel-scale-factor=4
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/iceland_step_1.png --size=128,80 --center=-18.7,65 --scale=5800 --rotation=0
	poetry run python map_generator/step_2_grayscale_to_1bit.py output/iceland_step_1.png output/iceland_step_2.png --mode=custom_1
	poetry run python map_generator/step_3_land_shadow.py output/iceland_step_2.png output/iceland_step_3.png
	poetry run python map_generator/step_4_sea_grayscale_utm_map.py output/iceland_step_3.png output/iceland_step_4.png --size=128,80 --center=-18.7,65 --scale=5800 --rotation=0 --max-depth=3500
	poetry run python map_generator/step_5_sea_2.py output/iceland_step_3.png output/iceland_step_4.png data/north_sea_map_brightness_tile_proportion.csv data/world_map_max_tile_counts.csv output/iceland_step_5.png

greece_example:
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/greece_step_1_x4.png --pixel-scale-factor=4 --size=128,80 --center=22,37.5 --scale=12500 --rotation=0
	poetry run python map_generator/step_1_land_grayscale_utm_map.py output/greece_step_1.png --size=128,80 --center=22,37.5 --scale=12500 --rotation=0
	poetry run python map_generator/step_2_grayscale_to_1bit.py output/greece_step_1.png output/greece_step_2.png --mode=custom_1
	poetry run python map_generator/step_3_land_shadow.py output/greece_step_2.png output/greece_step_3.png
	poetry run python map_generator/step_4_sea_grayscale_utm_map.py output/greece_step_3.png output/greece_step_4.png --max-depth=4400 --size=128,80 --center=22,37.5 --scale=12500 --rotation=0
	poetry run python map_generator/step_5_sea_2.py output/greece_step_3.png output/greece_step_4.png data/greece_map_brightness_tile_proportion.csv data/greece_map_max_tile_counts.csv output/greece_step_5.png

lint: ## Checks for linting errors
	poetry run flake8

update-engraver: ## upgrades map-engraver to latest version of master
	poetry remove map-engraver || true
	poetry add git+https://github.com/leifgehrmann/map-engraver.git
	poetry install
