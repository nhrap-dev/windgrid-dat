import pandas as pd
import os
from shapely.geometry import Point
import geopandas as gpd
import importlib
from utils import geodataframe_to_dat
from config import latitude_field, longitude_field, input_dir, output_dir

def csv_to_dat():
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid .csv or excel file
    """
    # list input files
    input_files = [x for x in os.listdir(input_dir) if x.endswith('.csv') or x.endswith('.xls') or x.endswith('.xlsx') or x.endswith('.xlsm') or x.endswith('.xlsb') or x.endswith('.odf') or x.endswith('.ods') or x.endswith('.odt')]

    for input_file in input_files:
        # read input files
        if input_file.endswith('.csv'):
            df = pd.read_excel(f'{input_dir}/{input_file}')
        else:
            df = pd.read_excel(f'{input_dir}/{input_file}')
        # create point geometry
        df['geometry'] = [Point(x, y) for x, y in zip(df[longitude_field], df[latitude_field])]
        # create geodataframe
        gdf = gpd.GeoDataFrame(df, geometry='geometry')
        # generate .dat file
        geodataframe_to_dat(gdf, f"{output_dir}/{'.'.join(input_file.split('.')[0:-1])}")

if __name__=='__main__':
    csv_to_dat()