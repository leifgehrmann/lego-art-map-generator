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
	convert readme_files/land_custom.png -filter box -resize 384x240 readme_files/land_custom_x3.png
	convert readme_files/land_dither.png -filter box -resize 384x240 readme_files/land_dither_x3.png
	convert readme_files/land_grayscale.png -filter box -resize 384x240 readme_files/land_grayscale_x3.png
	convert readme_files/land_lego.png -filter box -resize 384x240 readme_files/land_lego_x3.png
	convert readme_files/land_threshold.png -filter box -resize 384x240 readme_files/land_threshold_x3.png

output_example:
	poetry run python map_generator/step_1_land_grayscale_world_map.py output/example_step_1.png
	poetry run python map_generator/step_2_grayscale_to_1bit.py output/example_step_1.png output/example_step_2.png --mode=custom_1
	poetry run python map_generator/step_3_land_shadow.py output/example_step_2.png output/example_step_3.png
	poetry run python map_generator/step_4_sea_grayscale_world_map.py output/example_step_3.png output/example_step_4.png

lint: ## Checks for linting errors
	poetry run flake8

update-engraver: ## upgrades map-engraver to latest version of master
	poetry remove map-engraver || true
	poetry add git+https://github.com/leifgehrmann/map-engraver.git
	poetry install
