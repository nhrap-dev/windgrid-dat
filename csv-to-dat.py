import pandas as pd
# TODO code this based on arcgrid-to-dat.py
def csv_to_dat(windgrid_file, DAT_header, output_file, wind_field='gust_mph', latitude_field='lat', longitude_field='lon'):
    """ Creates a Hazus DAT file containing windspeeds in m/s from a windgrid csv file

    Keyword arguments:
        windgrid_file: str -- file location of windgrid csv
        DAT_header: list<str> -- a list of strings to be used as the header of the DAT file
        output_file: str -- file location and name of output DAT file
        wind_field: str -- the column or field name of the wind values to include in the DAT file
        latitude_field: str -- the column or field name for the latitude coordinates (use WGS84)
        longitude_field: str -- the column or field name for the longitude coordinates (use WGS84)
    """
    df = pd.read_csv(windgrid_file)
    df['geometry'] = [Point(x, y) for x, y in zip(
        df[longitude_field], df[latitude_field])]
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    create_dat_from_geodataframe(
        gdf, DAT_header, output_file, wind_field=wind_field)

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
        csv_to_dat(dat_header)