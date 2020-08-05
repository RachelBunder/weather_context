import boto3
import pandas as pd
import io

def get_historical_data(bucket, loc):
    ''' Reads a csv from S3 bucket with key loc and returns a pandas dataframe
    '''
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=loc)

    historical_data = pd.read_csv(io.BytesIO(obj['Body'].read()))

    return historical_data

def plt_to_s3(ax, bucket, plot_loc):
    ''' Takes matplotlib ax type and saves it to S3 bucket with location.
    Returns the saved object
    '''

    buf = io.BytesIO()
    ax.figure.savefig(buf, format="png")
    buf.seek(0)
    image = buf.read()

    # put the image into S3
    s3 = boto3.resource('s3')
    obj =  s3.Object(bucket, plot_loc).put(Body=image)

    return obj

def json_to_s3(json_str, bucket, loc):
    '''Saves json string to s3 bucket. Returns teh saved object'''
    s3 = boto3.client('s3')

    obj = s3.put_object(Body=json_str,
                        Bucket=bucket,
                        ContentType='application/json',
                        Key=loc
                       )

    return obj

