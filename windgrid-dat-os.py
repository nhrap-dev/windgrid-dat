import geopandas as gpd
import pandas as pd
from time import time
import numpy as np
# import matplotlib.pyplot as plt
# import os

def distance_matrix(x, y, xi, yi):
    """ Creates a matrix with the distance from a given point (x1, y1)
    to all other points

    Keyword arguments:
        x: 1d array -- point locations on the x-axis
        y: 1d array -- point locations on the y-axis
        xi: float -- x-axis point location of unknown value
        yi: float -- y-axis point location of unknown value
    
    Return:
        dist_mx: 1d array -- distances from every x,y point to xi,yi
    """
    obs = np.vstack((x, y)).T
    interp = np.vstack((xi, yi)).T

    # Make a distance matrix between pairwise observations
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    dist_mx = np.hypot(d0, d1)
    return dist_mx

def idw(x,y,z,xi,yi):
    """ Inverse Distance Weighting - interpolates an unknown value at a 
    specified point by weighting the values of it's nearest neighbors

    Keyword arguments:
        x: 1d array -- point locations on the x-axis
        y: 1d array -- point locations on the y-axis
        z: 1d array -- point values at each location
        xi: float -- x-axis point location of unknown value
        yi: float -- y-axis point location of unknown value
    
    Returns:
        zi: float -- interpolated value at xi, yi

    """
    neighbors = 12
    power = 2
    dist_all = distance_matrix(x,y, xi,yi)
    dist_n = np.asarray([np.sort(dist_all, axis=None)[x] for x in range(neighbors)])
    indicies = [np.where(dist_all == x)[0][0] for x in dist_n]
    z_n = z[indicies]
    if 0 not in dist_n:
        weights = power / dist_n
    else:
        dist_n += 0.000000001
        weights = power / dist_n
    weights /= weights.sum(axis=0)
    zi = np.dot(weights.T, z_n)
    return zi

def create_dat(windgrid_file, DAT_header, output_file):
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid shapefile

    Keyword arguments:
        windgrid_file: str -- file location of windgrid shapefile
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
    """
    t0 = time()
    output_file = output_file + '.dat'
    print('reading windgrid')
    t1 = time()
    windgrid = gpd.read_file(windgrid_file)
    print(time() - t1)
    print('reading us centroids')
    t1 = time()
    centroids_all = gpd.read_file('base_data/us_centroids.shp')
    print(time() - t1)

    print('selecting centroids in windgrid')
    t1 = time()
    buff = windgrid.geometry.buffer(0.2)
    buff_gdf = gpd.GeoDataFrame(geometry=buff.geometry)
    buff_gdf['dis'] = 1
    dissolve = buff_gdf.dissolve(by='dis')
    centroids_intersect = centroids_all.intersects(dissolve.unary_union)
    centroids = centroids_all[centroids_intersect == True]
    print(time() - t1)

    # fig, ax = plt.subplots()
    # dissolve.plot(ax=ax, color='white', edgecolor='black')
    # centroids.plot(ax=ax, marker='o', color='red', markersize=2)
    # plt.show()

    print('formatting data for idw')
    t1 = time()
    x = np.asarray([x.x for x in windgrid.geometry])
    y = np.asarray([x.y for x in windgrid.geometry])
    z = np.asarray([x for x in windgrid.Vg_mph])
    xis = np.asarray([x.x for x in centroids.geometry])
    yis = np.asarray([x.y for x in centroids.geometry])
    print(time() - t1)

    print('interpolating values')
    t1 = time()
    zis = []
    for xi, yi in zip(xis, yis):
        zi = idw(x,y,z,xi,yi)
        zis.append(zi)
    print(time() - t1)
    zis = np.asarray(zis) * 0.44704

    print('formatting dataframe for output')
    t1 = time()
    tracts = list(map(lambda x: x + '    ', centroids.TRACT))
    longs = list(map(lambda x: '{0:.4f}'.format(x) + '   ', xis))
    lats = list(map(lambda x: '{0:.4f}'.format(x) + '      ', yis))
    windSpeeds = list(map(lambda x: '{0:.5f}'.format(x) + '     ', zis))
    zeros = list(map(lambda x: '0' + '{0:.5f}'.format(x * 0) + '    ', zis))
    windSpeedsLast = list(map(lambda x: '{0:.5f}'.format(x), zis))
    df = pd.DataFrame({'tracts': tracts, 'longs': longs, 'lats': lats, 'windSpeeds': windSpeeds, 'zeros': zeros, 'windSpeedsLast': windSpeedsLast})
    print(time() - t1)

    print('writing output DAT file')
    t1 = time()
    # creates and opens the export DAT file
    pd.DataFrame().to_csv(output_file, header=False, index=False)
    export=open(output_file, "w")

    # adds columns to the DAT file header
    DAT_header.append('')
    DAT_header.append('      ident        elon      nlat         ux          vy        w (m/s)')

    # writes header to DAT file
    for row in DAT_header:
        export.write(row + '\n')

    # writes data to DAT file
    for row in range(len(df[df.columns[0]])):
        writeRow = ''
        for item in df.iloc[row]:
            writeRow = writeRow + item
        export.write(writeRow + '\n')
    export.close()
    print(time() - t1)
    print('Total elasped time: ' + str(time() - t0))


windgrid_file = 'wind_grid/wind_grid.shp'
DAT_header = ['Florence 2018: ARA Day7 as of 09/21/2018',
'MAXIMUM 3 SECOND WINDS AT 2010 CENSUS TRACK CENTROIDS FOR OPEN TERRAIN',
'Swath domain provided by FEMA',
'Landfall position:     -77.8001      34.2001']
output_file = 'output'

create_dat(windgrid_file, DAT_header, output_file)