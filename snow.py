import boto3
import json
import logging
import os

from base64 import b64decode
from urlparse import parse_qs

from lxml import html
import requests


ENCRYPTED_EXPECTED_TOKEN = os.environ['kmsEncryptedToken']

kms = boto3.client('kms')
expected_token = kms.decrypt(CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_TOKEN))['Plaintext']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token %s) does not match expected", token)
        return respond(Exception('Invalid request token'))

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    command_text = params['text'][0]
   
    if command_text == 'hood':
        results = hood_meadows()
    else:
        results = hood_meadows()

    return respond(None, results)

def hood_meadows():
    page = requests.get('https://www.skihood.com/the-mountain/conditions')
    tree = html.fromstring(page.content)

    headers = tree.xpath('//div[@class="conditions-glance-widget conditions-snowfall"]/dl/dt/text()')
    data = tree.xpath('//div[@class="conditions-glance-widget conditions-snowfall"]/dl/dd/text()')

    out = ''

    for i, header in enumerate(headers, start=0):
        out += "%s: %sin. " % (header, data[i])

    return out
