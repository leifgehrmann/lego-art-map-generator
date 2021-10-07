import os
import shutil
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from urllib.error import HTTPError
import click


@click.command()
@click.argument(
    'url',
    nargs=1
)
@click.argument(
    'destination',
    nargs=1,
    type=click.Path(exists=True)
)
def natural_earth(url, destination):
    # Declare file paths. The filenames are inferred from the url, so this
    # logic could be brittle to changes.
    zip_name = url.split('/')[-1]
    extract_name = url.split('/')[-1].split('.')[0]
    destination_path = Path(destination)
    zip_path = destination_path.joinpath(zip_name)
    extract_path = destination_path.joinpath(extract_name)

    # Download the ZIP to the cache.
    attempts = 0
    while attempts < 5:
        try:
            data = urllib.request.urlopen(url)
            data = data.read()
            file = open(zip_path.as_posix(), 'wb')
            file.write(data)
            file.close()
            break
        except HTTPError as e:
            if attempts == 4:
                raise e
            attempts += 1

    # Extract the ZIP within the cache.
    with zipfile.ZipFile(zip_path.as_posix()) as zf:
        zf.extractall(extract_path.as_posix())

    # Move Shapefile out of the extract directory to the destination directory.
    for file_type in ['shp', 'dbf']:
        file_name = extract_name + '.' + file_type
        extract_file_type_path = extract_path.joinpath(file_name)
        destination_file_type_path = destination_path.joinpath(file_name)
        os.rename(
            extract_file_type_path.as_posix(),
            destination_file_type_path.as_posix()
        )

    # Delete ZIP and Extract.
    os.unlink(zip_path.as_posix())
    shutil.rmtree(extract_path.as_posix())


if __name__ == '__main__':
    natural_earth()
