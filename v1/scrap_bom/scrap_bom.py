import json
import requests
import pandas as pd
import boto3

from lxml.html import fromstring
from io import StringIO
from datetime import date

from localities import S3_BUCKET, HISTORICAL_OBS_LOC

def get_today_data():
    '''Scarps the BOM website for the current max, min and rainfall
    '''
    url =  'http://reg.bom.gov.au/nsw/observations/sydney.shtml'
    page = requests.get(url)

    # Getting page data
    tree = fromstring(page.content)
    data_date = tree.xpath('//td[@headers="tSYDNEY-datetime tSYDNEY-station-sydney-observatory-hill"]/text()')[0]
    maxT = float(tree.xpath('//td[@headers="tSYDNEY-hightmp tSYDNEY-station-sydney-observatory-hill"]/text()')[0])
    minT = float(tree.xpath('//td[@headers="tSYDNEY-lowtmp tSYDNEY-station-sydney-observatory-hill"]/text()')[0])
    rain = float(tree.xpath('//td[@headers="tSYDNEY-rainsince9am tSYDNEY-station-sydney-observatory-hill"]/text()')[0])


    # Fixing up the date as it is in day/time format
    # Not using exclusively date.today() as I do want to be careful about
    # timzone problems
    day = int(data_date.split('/')[0])
    today = date.today()
    data_date = today.replace(day=day)

    # Adding it to the historical reading
    recent_obs = pd.DataFrame({'Year':data_date.year,
                               'Month':data_date.month,
                               'Day': data_date.day,
                               'Maximum temperature (°C)':maxT,
                               'Minimum temperature (°C)':minT,
                               'Rainfall (mm)':rain},
                               index=[0])
    return recent_obs


def lambda_handler(event, context):
    # Get most recent observations for this month
    recent_obs = get_today_data()

    # Read historical data from S3
    s3 = boto3.resource('s3')
    historical_obs_loc = s3.Object(bucket_name=S3_BUCKET, key=HISTORICAL_OBS_LOC)
    historical_obs = pd.read_csv(historical_obs_loc.get()['Body'])

    # To keep this data frame up to date, we concatentate it with the most
    # recent month, then drop the earliest rows
    # (assumed more recent data is correct)
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

if __name__=='__main__':
    lambda_handler(None, None)
