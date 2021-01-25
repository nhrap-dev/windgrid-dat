from scipy.spatial import cKDTree
import geopandas as gpd
import pandas as pd
import os
import numpy as np
from config import wind_field, output_dir, dat_header

def idw(kdtree, z, xi, yi):
    """ Inverse Distance Weighting - interpolates an unknown value at a 
    specified point by weighting the values of it's nearest neighbors

    Keyword arguments:
        kdtree: scipy.spatial.ckdtree -- kdtree made from a 2d array of x and y coordinates as the columns 
        z: 1d array -- point values at each location
        xi: float -- x-axis point location of unknown value
        yi: float -- y-axis point location of unknown value

    Returns:
        zi: float -- interpolated value at xi, yi

    """
    neighbors = 12
    power = 2
    distances, indicies = kdtree.query([xi, yi], k=neighbors)
    z_n = z[indicies]
    if 0 not in distances:
        weights = power / distances
    else:
        distances += 0.000000001
        weights = power / distances
    weights /= weights.sum(axis=0)
    zi = np.dot(weights.T, z_n)
    return zi

def mph_to_mps(mph):
    if type(mph) == str:
        mph = float(mph)
    conversion_const = 0.44704
    return mph * conversion_const

def calculate_windspeeds_at_centroids(windspeeds_gdf, tracts):
    # format data for kdtree and idw
    xy = np.asarray([[x.x, x.y] for x in windspeeds_gdf.geometry])
    z = np.asarray([x for x in windspeeds_gdf[wind_field]])
    xis = np.asarray([x.centroid.x for x in tracts.geometry])
    yis = np.asarray([x.centroid.y for x in tracts.geometry])
    
    # build kdtree
    kdtree = cKDTree(xy)
    zis = []
    for xi, yi in zip(xis, yis):
        # interpolate windspeed
        zi = idw(kdtree, z, xi, yi)
        zis.append(zi)
    zis = np.asarray(zis)
    # convert to meters/second
    zis = mph_to_mps(zis)
    return zis

def generate_dat_df(windspeeds_array, tracts):
    df = pd.DataFrame()
    for index, tract in enumerate(list(tracts.geometry)):
        df = df.append({
            'ident': f"{tracts.loc[index]['GEOID']}    ",
            'elon': f"{'{0:.4f}'.format(float(tract.centroid.x))}   ",
            'nlat': f"{'{0:.4f}'.format(float(tract.centroid.y))}      ",
            'ux': f"{'{0:.5f}'.format(windspeeds_array[index])}     ",
            'vy': f"0{'{0:.5f}'.format(0)}    ",
            'w (m/s)': f"{'{0:.5f}'.format(windspeeds_array[index])}",
        }, ignore_index=True)

    df = df.reindex(columns=['ident', 'elon', 'nlat', 'ux', 'vy', 'w (m/s)'])
    return df

def write_dat_file(output_file, dat_df, dat_header):
        if not output_file.endswith('.dat'):
            output_file = f'{output_file}.dat'
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

def geodataframe_to_dat(gdf, output_file):
    # read data
    tracts = gpd.read_file('db/tracts/tracts.shp')

    # select tracts
    gdf['dissolve'] = 0
    gdf_convex_hull = gdf.dissolve(by='dissolve').convex_hull
    tracts_selection = tracts[tracts.geometry.intersects(gdf_convex_hull.geometry[0])]
    tracts_selection = tracts_selection.reset_index()

    # calculate windspeeds
    windspeeds_array = calculate_windspeeds_at_centroids(gdf, tracts_selection)

    # generate dat df
    dat_df = generate_dat_df(windspeeds_array, tracts_selection)

    # write to .dat file
    write_dat_file(output_file, dat_df, dat_header)