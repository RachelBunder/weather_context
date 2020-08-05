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

    print({
        'statusCode': 200,
        'body': f"tweet succeeded, {str(event)}",
        'tweet_status': status,
        'tweet_json': json.dumps(tweet_json)
    })
    return {
        'statusCode': 200,
        'body': f"tweet succeeded, {str(event)}",
        'tweet_status': status,
        'tweet_json': json.dumps(tweet_json)
    }

event = {
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "ap-southeast-2",
      "eventTime": "2020-05-16T20:51:28.554Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AJUMLNLUY38U"
      },
      "requestParameters": {
        "sourceIPAddress": "119.18.3.228"
      },
      "responseElements": {
        "x-amz-request-id": "EA36DDCEDB710CE7",
        "x-amz-id-2": "wexLF0IijnquCctyPWZ28RTnew7oNQCMbv5O9bj7k6Ti+aYOTmKN1sLATLinn5eZLMQ/1JdRgFsr1Ryij3MBrO/SAxQs5hF4"
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "bad1dca8-147d-4887-a599-98c9228f4d2d",
        "bucket": {
          "name": "bom-bot",
          "ownerIdentity": {
            "principalId": "AJUMLNLUY38U"
          },
          "arn": "arn:aws:s3:::bom-bot"
        },
        "object": {
          "key": "tweets/2020-08-05-maximum.json",
          "size": 165,
          "eTag": "38b30c2fb26a92da7230e17539149db3",
          "sequencer": "005EC052517BF7719A"
        }
      }
    }
  ]
}
if __name__ == '__main__':
    lambda_handler(event, None)
