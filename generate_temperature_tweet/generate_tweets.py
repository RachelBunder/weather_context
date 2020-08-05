import json
import pandas as pd
import boto3
import io
from datetime import date
import os
import json

from plot_functions import plot_time_series, plot_distribution, distribution_alt_text
from s3_functions import get_historical_data, plt_to_s3, json_to_s3

from localities import S3_BUCKET, HISTORICAL_OBS_LOC, TWEET_PATH, TWEET_MEDIA_PATH


def get_temp_summary(historical_today, kind, today):
    ''' Generates text for a temperature tweet. The text format is:
    f"Today's {kind} temperature, {today_temp}C, was {likelihood_statement} at
    {avg_diff:.1f}C {avg_change} the average. It is the{rank_phrase}
    {descriptor} recorded {kind} for the {date}"


    historical_today: dataframe with the day's historical data
    kind: either 'minimum' or 'maximum'
    today: the date we are compaing with

    '''

    # Get the today's data
    if kind=='maximum':
        col = 'Maximum temperature (°C)'
        historical_today['rank'] = historical_today[col].rank(method='max')
    elif kind=='minimum':
        col = 'Minimum temperature (°C)'
        historical_today['rank'] = historical_today[col].rank(method='max')
    else:
        return

    # If today's data is not in yet
    today_temp = historical_today.loc[historical_today['Year']==today.year, col].values[0]

    if pd.isna(today_temp):
        return None

    # Less or more than average
    avg_diff = historical_today[col].mean() - today_temp
    if avg_diff < 0:
        avg_diff = -avg_diff
        avg_change = 'over'
    else:
        avg_change = 'below'

    # calculating rank
    rank = historical_today.loc[historical_today['Year']==today.year, 'rank'].values[0]

    num_records = len(historical_today[col].dropna())
    if rank < num_records//2:
        descriptor = 'coldest'
        rank = rank + 1
    else:
        descriptor = 'hotest'
        rank = num_records - rank + 1

    suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n%100<20 else n%10,"th"))
    date = f'{suf(today.day)} of {today.strftime("%B")}'

    rank_phrase = '' if rank==1 else ' ' + suf(rank)

    # Calculating zscore
    mean = historical_today[col].mean()
    std = historical_today[col].std()

    z = (today_temp - mean)/std

    if abs(int(z)) == 0:
        likelihood_statement = "very likely"
    elif abs(int(z)) == 1:
        likelihood_statement = "likely"
    elif abs(int(z)) == 2:
        likelihood_statement = "unlikely"
    else:
        likelihood_statement = "very unlikely"

    text = f"Today's {kind} temperature, {today_temp}C, was {likelihood_statement} at {avg_diff:.1f}C {avg_change} the average. It is the{rank_phrase} {descriptor} recorded {kind} for the {date}"

    return text

def lambda_handler(event, context):
    ''' Creates JSON file containing tweet info for the the maximum and minimum
    temperature in context'''

    # Getting historical data
    today = date.today()

    kind=event['kind']
    historical_data = get_historical_data(S3_BUCKET, HISTORICAL_OBS_LOC)
    historical_today = historical_data[(historical_data['Month']==today.month)&
                                       (historical_data['Day']==today.day)].dropna()

    # Get text for tweet
    summary = get_temp_summary(historical_today,
                               kind=kind,
                               today=today)

    # If no text, then no data
    if summary is None:
        return {
        'statusCode': 404,
        'body': json.dumps(f'No data for today {today.year}-{today.month}-{today.day}')
    }

    # Create plots
    ax_timeseries, timeseries_alt = plot_time_series(historical_today,
                                                      kind,
                                                      today)
    timeseries_loc = os.path.join(TWEET_MEDIA_PATH,
                                  today.strftime(f'%Y-%m-%d-{kind}-timeseries.png'))
    plt_to_s3(ax_timeseries, S3_BUCKET, timeseries_loc)

    ax_distplot, distplot_alt = plot_distribution(historical_today, kind, today)
    distplot_loc = os.path.join(TWEET_MEDIA_PATH,
                                today.strftime(f'%Y-%m-%d-{kind}-distplot.png'))
    plt_to_s3(ax_distplot, S3_BUCKET, distplot_loc)


    # Collate data and save to s3
    tweet_data = json.dumps({'body':summary,
                             'media': [timeseries_loc, distplot_loc],
                             'alt_text': [timeseries_alt, distplot_alt]})

    json_loc = os.path.join(TWEET_PATH, today.strftime(f'%Y-%m-%d-{kind}.json'))
    json_to_s3(tweet_data, S3_BUCKET, json_loc)

    return {
        'statusCode': 200,
        'body': json.dumps(f'Created tweet {str(tweet_data)} stored at {json_loc}')
    }
