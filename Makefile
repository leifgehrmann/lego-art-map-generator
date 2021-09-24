.PHONY: help
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
	poetry run python lego_art_map_generator/natural_earth.py \
	https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip \
	data
	poetry run python lego_art_map_generator/natural_earth.py \
	https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_lakes.zip \
	data

lint: ## Checks for linting errors
	poetry run flake8

update-engraver: ## upgrades map-engraver to latest version of master
	poetry remove map-engraver || true
	poetry add git+https://github.com/leifgehrmann/map-engraver.git
	poetry install
