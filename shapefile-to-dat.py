import pandas as pd
import os
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import importlib
from utils import geodataframe_to_dat
from config import latitude_field, longitude_field, input_dir, output_dir

def shapefile_to_dat():
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid point or polygon Shapefile
    """
    # list input files
    input_files = [x for x in os.listdir(input_dir) if x.endswith('.shp')]

    for input_file in input_files:
        # read input files
        gdf = gpd.read_file(f'{input_dir}/{input_file}')
        if type(gdf['geometry'][0]) != Point:
            gdf['geometry'] = [x.centroid for x in gdf['geometry']]
        # generate .dat file
        geodataframe_to_dat(gdf, f"{output_dir}/{'.'.join(input_file.split('.')[0:-1])}")

if __name__=='__main__':
    shapefile_to_dat()