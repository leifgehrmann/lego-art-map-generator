import csv
import sys
from pathlib import Path
import re

tile_count = {}
total_count = 0

# Grab all the file names passed in as arguments
files = sys.argv[1:]

def strip_ascii_grid_header(ascii_grid_contents: str) -> str:
    """
    If the the file is an .asc file (ASCII Grid), then we want to ignore
    the headers from the top of the file. We do this by assuming that every
    line that contains a non-numeric character is a header row, and that any
    row with a number is a data row.
    """
    match = re.search(r"^\d[^a-z\n]+$", ascii_grid_contents, re.MULTILINE)
    if match:
        index = match.start()
        return ascii_grid_contents[index:]
    raise Exception('Unexpected contents of ASCII Grid file')

# Parse every ASCII Grid file
contents_arr = []
for file in files:
    contents_str = strip_ascii_grid_header(Path(file).read_text())
    contents_arr = csv.reader(contents_str.splitlines(), delimiter=' ')

    # Tally up the number of tiles for each tile 'name'
    for contents_arr_row in contents_arr:
        for tile_name in contents_arr_row:
            if tile_name in tile_count:
                tile_count[tile_name] += 1
            else:
                tile_count[tile_name] = 1
            total_count += 1

# Print out the totals, sorted alphabetically
for tile_name in [i for i in sorted(tile_count.keys(), key=int)]:
    print(tile_name, tile_count[tile_name])

print('total', total_count)
