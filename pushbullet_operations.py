from models import Users
import requests
import api_endpoints
import json

config = json.loads(open('config.json').read())


def check_current_user_data(username):
    access_token = Users.objects(username=username).first().pn_access_token

    headers = {
        'Access-Token': access_token,
        'Content-Type': 'application/json'
    }

    response = requests.get(api_endpoints.PUSHBULLET_CURRENT_USER_ENDPOINT, headers=headers).json()
    return response


def get_access_token(code):
    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        'grant_type': 'authorization_code',
        'client_id': config['PUSHBULLET_CLIENT_ID'],
        'client_secret': config['PUSHBULLET_CLIENT_SECRET'],
        'code': code
    }

    response = requests.post(api_endpoints.PUSHBULLET_ACCESS_TOKEN_ENDPOINT, headers=headers, json=data).json()
    return response['access_token']


def send_push_notification(product, lastest_price):
    access_token = Users.objects(username=product.username).first().pn_access_token

    headers = {
        'Access-Token': access_token,
        'Content-Type': 'application/json'
    }

    data = {
        'type': 'link',
        'title': 'Prices dropped ! Hurry !',
        'body': 'Prices for product with ASIN {} has dropped below threshold to {}. Click here for more information.'.format(product.asin, lastest_price),
        'url': product.product_url
    }

    response = requests.post(api_endpoints.PUSHBULLET_CREATE_PUSH_ENDPOINT, headers=headers, json=data).json()
    return response