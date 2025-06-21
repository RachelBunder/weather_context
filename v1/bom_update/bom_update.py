import json
import requests
import pandas as pd
import boto3
from io import StringIO
from datetime import date

from localities import S3_BUCKET, HISTORICAL_OBS_LOC

def get_month_data(year_month, station='IDCJDW2124'):
    '''Get the daily min, max temperatures and rainfall for each day in
    year_month

    Inputs:
        year_month: Month to get observations for in YYYYMM format
        station: which BOM weather station. Default if Observatory hill
    Output:
        DataFrame with the min, max temperatures and rainfall for each day so
          for in year_month
    '''
    year_month = date.today().strftime('%Y%m')
    response = requests.get(f'http://www.bom.gov.au/climate/dwo/{year_month}/text/{station}.{year_month}.csv')

    recent_obs = pd.read_csv(StringIO(response.text),
                             skiprows=9,
                             usecols=['Date',
                                      'Minimum temperature (°C)',
                                      'Maximum temperature (°C)',
                                      'Rainfall (mm)'],
                             parse_dates=['Date'])


    recent_obs['Year'] = recent_obs['Date'].dt.year
    recent_obs['Month'] = recent_obs['Date'].dt.month
    recent_obs['Day'] = recent_obs['Date'].dt.day

    return recent_obs[['Year',
                       'Month',
                       'Day',
                       'Minimum temperature (°C)',
                       'Maximum temperature (°C)',
                       'Rainfall (mm)']]


def lambda_handler(event, context):
    # Get most recent observations for this month
    year_month = year_month = date.today().strftime('%Y%m')
    recent_obs = get_month_data(year_month)

    # Read historical data from S3
    s3 = boto3.resource('s3')
    historical_obs_loc = s3.Object(bucket_name=S3_BUCKET,
                                   key=HISTORICAL_OBS_LOC)
    historical_obs = pd.read_csv(historical_obs_loc.get()['Body'])

    # To keep this data frame up to date, we concatentate it with the most recent
    # month, then drop the earliest rows (assumed more recent data is correct)
    historical_obs = pd.concat([historical_obs, recent_obs])
    historical_obs = historical_obs.drop_duplicates(['Year', 'Month', 'Day'],
                                                    keep='last')

    # Finally upload back to S3
    csv_buffer = StringIO()
    historical_obs.to_csv(csv_buffer, index=False)
    s3.Object(S3_BUCKET, HISTORICAL_OBS_LOC).put(Body=csv_buffer.getvalue())

    return {
        'statusCode': 200,
        'body': json.dumps(recent_obs.to_dict('records'))
    }