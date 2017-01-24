from models import *
import requests
import api_endpoints
import json

config = json.loads(open('config.json').read())

def check_current_user_data(username):
    access_token = Users.objects(username = username).first().access_token

    headers = {
        'Access-Token' : access_token,
        'Content-Type' : 'application/json'
    }

    response = requests.get(api_endpoints.PUSHBULLET_CURRENT_USER_ENDPOINT, headers = headers).json()
    return response

def get_access_token(code):

    headers = {
        'Content-Type' : 'application/json'
    }

    data = {
        'grant_type' : 'authorization_code',
        'client_id' : config['PUSHBULLET_CLIENT_ID'],
        'client_secret' : config['PUSHBULLET_CLIENT_SECRET'],
        'code' : code
    }

    response = requests.post(api_endpoints.PUSHBULLET_ACCESS_TOKEN_ENDPOINT, headers=headers, json=data).json()
    return response['access_token']
