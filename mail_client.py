from models import Users

import requests
import json

config = json.loads(open('config.json').read())
domain = 'monitora.ml'


def is_verified_email(email):
    data = {
        'address': email
    }

    response = requests.get('https://api.mailgun.net/v3/address/validate', auth=('api', config['MAILGUN_PUBLIC_SECRET_KEY']), data=data).json()
    return response['is_valid']


def send_email(product, latest_price):
    recipient = Users.objects(username=product.username).first().email

    data = {
        'from': 'Monitor-A <no-reply@monitora.ml>',
        'to': recipient,
        'subject': 'Prices Dropped ! Hurry !',
        'text': 'Dear User,\nPrices for product with ASIN {} has dropped below threshold to {}. Click on the link below for more information.\n{}'.format(product.asin, latest_price, product.product_url)
    }

    response = requests.post('https://api.mailgun.net/v3/{}/messages'.format(domain), auth=('api', config['MAILGUN_PRIVATE_SECRET_KEY']), data=data)
