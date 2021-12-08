import csv
from pathlib import Path
from typing import Dict


class BrightnessTileProportions:

    @staticmethod
    def read_from_csv(
            csv_path: Path
    ) -> Dict[int, Dict[str, float]]:
        """
        Reads the tile distribution for each brightness level from
        distribution chart.
        """
        proportions = {}
        row_count = 0
        brightness_ranges = []
        with open(csv_path.as_posix()) as file:
            for row in csv.reader(file, delimiter=',', skipinitialspace=True):
                row_count += 1
                if row_count == 1:
                    brightness_ranges = row[1:]
                    continue

                tile = row[0]
                brightness_proportions = row[1:]
                last_end = 0

                for brightness_proportion_i in \
                        range(len(brightness_proportions)):
                    brightness_range_str = brightness_ranges[
                        brightness_proportion_i
                    ]
                    brightness_proportion = float(brightness_proportions[
                                                      brightness_proportion_i
                                                  ])
                    if '-' in brightness_range_str:
                        start_str, end_str = brightness_range_str.split('-')
                    else:
                        start_str = brightness_range_str
                        end_str = start_str
                    start = int(start_str)
                    end = int(end_str)

                    # Back-fill any values
                    if last_end != start:
                        for brightness in range(last_end, start):
                            print(brightness, last_end, start)
                            if brightness not in proportions:
                                proportions[brightness] = {}
                            interpolated_perc = (brightness - last_end) / (
                                    start - last_end)
                            print('intperc',interpolated_perc)
                            last_end_prop = proportions[
                                last_end][tile]
                            interpolated_prop = \
                                (brightness_proportion - last_end_prop) * \
                                interpolated_perc + last_end_prop
                            print('last', last_end_prop)
                            print('start', brightness_proportion)
                            print('intprop', interpolated_prop)
                            proportions[brightness][tile] = interpolated_prop

                    for brightness in range(start, end + 1):
                        if brightness not in proportions:
                            proportions[brightness] = {}
                        proportions[brightness][tile] = brightness_proportion

                    last_end = end

        # Normalise the proportions to be between 0 and 1
        for brightness, tile_proportions in proportions.items():
            tile_proportion_sum = sum(tile_proportions.values())
            for tile, proportion in tile_proportions.items():
                proportions[brightness][tile] = proportion / \
                                                tile_proportion_sum

        return proportions
