import geopandas as gpd
import rasterio as rio
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from rasterio.features import shapes
from rasterio.mask import mask
from shapely.geometry import shape
from shapely.ops import cascaded_union
import os
import pandas as pd
import sys
from datetime import datetime

def getValueMask(src):
    mask = None
    image = src.read(1) # first band
    nonZeroMask = np.where(image > 0, 1, 0)
    _shapes = [shape(s) for s, v in shapes(nonZeroMask, transform=src.transform) if v > 0]
    union = cascaded_union(_shapes)
    return union

def mph_to_mps(mph):
    if type(mph) == str:
        mph = float(mph)
    conversion_const = 0.44704
    return mph * conversion_const

def generate_dat_df(src, tracts):
        df = pd.DataFrame()
        for index, tract in enumerate(list(tracts.geometry)):
            rasterMask, rasterMaskTransform = mask(dataset=src, shapes=[tract], all_touched=False, crop=True, nodata=0)
            mean = np.mean(rasterMask[0])
            mean = mph_to_mps(mean)
            if mean > 0:
                df = df.append({
                    'ident': f"{tracts.loc[index]['GEOID']}    ",
                    'elon': f"{'{0:.4f}'.format(float(tracts.loc[index]['geometry'].centroid.x))}   ",
                    'nlat': f"{'{0:.4f}'.format(float(tracts.loc[index]['geometry'].centroid.y))}      ",
                    'ux': f"{'{0:.5f}'.format(mean)}     ",
                    'vy': f"0{'{0:.5f}'.format(0)}    ",
                    'w (m/s)': f"{'{0:.5f}'.format(mean)}",
                }, ignore_index=True)
        
        df = df.reindex(columns=['ident', 'elon', 'nlat', 'ux', 'vy', 'w (m/s)'])
        return df

def write_dat_file(output_file, dat_df, dat_header):
        with open(output_file, "w") as export:
            # adds columns to the DAT file header
            dat_header.append('')
            dat_header.append(
                '      ident        elon      nlat         ux          vy        w (m/s)')

            # writes header to DAT file
            for row in dat_header:
                export.write(row + '\n')

            # writes data to DAT file
            for row in range(len(dat_df[dat_df.columns[0]])):
                writeRow = ''
                for item in dat_df.iloc[row]:
                    writeRow = writeRow + item
                export.write(writeRow + '\n')


def arcgrid_to_dat(dat_header):
    in_path_base = 'input'
    out_path_base = 'output'
    rasters = [x for x in os.listdir(in_path_base) if '.' not in x]
    tracts = gpd.read_file('db/tracts/tracts.shp')
    for raster in rasters:
        try:
            src = rio.open(f'{in_path_base}/{raster}')
            valueMask = getValueMask(src)
            intersect = tracts.geometry.intersects(valueMask)
            tractsSelection = tracts[intersect]
            tractsSelection = tractsSelection.reset_index()
            df = generate_dat_df(src, tractsSelection)
            output_file = f'{out_path_base}/{raster}.dat'
            write_dat_file(output_file, df, dat_header)
        except Exception as e:
            print(e)


if __name__=='__main__':
    if len(sys.argv) > 1:
        name = sys.argv[1]
        try:
            date = sys.argv[2]
        except:
            date = datetime.now()
        date_format = "%m/%d/%Y"
        date = date.strftime(date_format)
        dat_header = [f'{name}: ARA Wind Model as of {date}',
            'PEAK 3-SECOND GUSTS AT 10 M OVER FLAT, OPEN TERRIAN',
            'Swath domain provided by FEMA']
        arcgrid_to_dat(dat_header)