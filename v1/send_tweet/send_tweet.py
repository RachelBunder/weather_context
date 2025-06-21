import json
import tweepy
import boto3
import io

from twitter_secrets import C_KEY, C_SECRET, A_TOKEN, A_TOKEN_SECRET

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
twitter_api = tweepy.API(auth)

def tweet_media(text, media, alt):
    """Send out the text + media as a tweet."""


    # Send the tweet and log success or failure
    try:
        s3 = boto3.resource('s3')
        # get plots from s3
        filenames = [f'/tmp/{i.split("/")[-1]}' for i in media]
        for i, image in enumerate(media):
            s3.Bucket('bom-bot').download_file(image, filenames[i])

        # Upload plots
        media_ids = [twitter_api.media_upload(image).media_id_string for image in filenames]

        # Add alt text
        for m, media_id in enumerate(media_ids):
            twitter_api.create_media_metadata(media_id, alt[m])

        # Send tweet
        tweet_deets = twitter_api.update_status(status=text, media_ids=media_ids)
    except tweepy.error.TweepError as e:
        return str(e)

    return 200


def lambda_handler(event, context):

    s3_details = event['Records'][0]['s3']
    bucket = s3_details['bucket']['name']
    key = s3_details['object']['key']

    s3 = boto3.client('s3')
    json_object = s3.get_object(Bucket=bucket, Key=key)
    tweet_json = json.loads(json_object['Body'].read().decode('utf-8'))

    status = tweet_media(tweet_json['body'],
                         tweet_json['media'],
                         tweet_json['alt_text'])


    return {
        'statusCode': 200,
        'body': f"tweet succeeded, {str(event)}",
        'tweet_status': status,
        'tweet_json': json.dumps(tweet_json)
    }
