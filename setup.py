import urllib.request
import io
import zipfile
import os
import geopandas as gpd
from shutil import rmtree
from config import input_dir, output_dir

def download_and_return_content(url, destination):
    print('downloading...')
    if not destination.endswith('.zip'):
        destination = destination + '.zip'
    if not os.path.isfile(destination):
        with urllib.request.urlopen(url) as response, open(destination, 'wb') as out:
            data = response.read() # a `bytes` object
            out.write(data)

def unzip(source, destination):
    print('extracting...')
    zip_ref = zipfile.ZipFile(source, 'r')
    zip_ref.extractall(destination)
    zip_ref.close()
    os.remove(source)

def setup_db():
    print('setting up database...')
    os.mkdir('db')
    source = 'https://www2.census.gov/geo/tiger/GENZ2019/shp/cb_2019_us_tract_500k.zip'
    destination = 'db/cb_2019_us_tract_500k'
    download_and_return_content(source, destination)
    unzip(f'{destination}.zip', destination)

    print('reprojecting...')
    tracts = gpd.read_file(f'{destination}/cb_2019_us_tract_500k.shp')
    tracts = tracts.to_crs('epsg:4326')
    os.mkdir('db/tracts')
    tracts.to_file('db/tracts/tracts.shp', driver="ESRI Shapefile")
    rmtree(destination)

def setup_directories():
    print('setting up directories...')
    os.mkdir(input_dir)
    os.mkdir(output_dir)

if __name__=='__main__':
    setup_db()
    setup_directories()
    print("""setup complete - you are free to use the scripts\n
        1) activate your venv with all dependencies\n
            Example: activate hazus_env\n
        2) copy the conversion files to the input folder (GTiff, CSV, Shapefile, ArcGrid)\n
        3) run the script in the terminal\n
            Syntax: python script.py dat_header_name dat_header_date  
            Example: python gtiff-to-dat.py "Hurricane Hanna" 09/08/2020\n
        4) view the .dat file(s) in the output folder
    """)