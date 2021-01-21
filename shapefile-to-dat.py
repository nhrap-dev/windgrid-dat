import geopandas as gpd
import geodataframe_to_dat from utils
# TODO code this based on arcgrid-to-dat.py
def shapefile_to_dat(windgrid_file, DAT_header, output_file, wind_field='Vg_mph'):
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid shapefile

    Keyword arguments:
        windgrid_file: str -- file location of windgrid shapefile
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
        wind_field: str -- the column or field name of the wind values to include in the DAT file
    """
    t0 = time()
    output_file = output_file + '.dat'
    print('reading windgrid')
    t1 = time()
    gdf = gpd.read_file(windgrid_file)
    geodataframe_to_dat(gdf, DAT_header, output_file, wind_field=wind_field)

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
        shapefile_to_dat(dat_header)