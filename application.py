from flask import Flask, render_template, session, redirect, url_for, jsonify, request
import time
import json
import uuid
import urllib
from passlib.hash import pbkdf2_sha256
from database_connection import *
from models import *
from amazon_operations import *
from pushbullet_operations import *
from schedular_operations import *
from database_operations import *
from utils import *

app = Flask(__name__)
config = json.loads(open('config.json').read())

@app.route('/')
def render_index():
    return render_template('index.html')


@app.route('/checkLoginStatus')
def check_login_status():
    return jsonify({'status' : 'username' in session})


@app.route('/login', methods=['POST'])
def check_login_credentials():
    credentials = request.get_json(force = True)

    try:
        if credentials['username'] and credentials['password']:
            valid_credentials = pbkdf2_sha256.verify(credentials['password'], Users.objects(username = credentials['username']).first().password)
        else:
            valid_credentials = False
    except:
        valid_credentials = False

    if valid_credentials:
        session['username'] = credentials['username']

    return jsonify({'status' : valid_credentials})


@app.route('/logout')
def logout_user():
    session.clear()
    return jsonify({'status' : 'username' not in session})


@app.route('/checkAccessTokenValidity')
def check_access_token_validity():
    response = check_current_user_data(session['username'])
    return jsonify({'status' : 'error' not in response})


@app.route('/checkUsernameValidity', methods=['POST'])
def check_username_validity():
    username = request.get_json(force=True)['username']
    users = Users.objects(username = username)
    return jsonify({'status': len(users) == 0})


@app.route('/checkEmailValidity', methods=['POST'])
def check_email_validity():
    email = request.get_json(force=True)['email']
    users = Users.objects(email = email)
    return jsonify({'status' : len(users) == 0})


@app.route('/signUpUser', methods=['POST'])
def sign_up_user():
    signup_data = request.get_json(force=True);
    username = signup_data['username']
    email = signup_data['email']
    password = pbkdf2_sha256.hash(signup_data['password'])

    user = Users(username=username, email=email, password=password)
    user.save()
    return jsonify({'status' : True})


@app.route('/getOAuthUrl')
def get_oauth_url():
    query_parameters = {
        'client_id' : config['PUSHBULLET_CLIENT_ID'],
        'redirect_uri' : 'https://2c3eff46.ngrok.io/oauth',
        'response_type' : 'code'
    }

    return jsonify({'status' : True, 'oauth_url' : api_endpoints.PUSHBULLET_OAUTH_ENDPOINT + "?" + urllib.parse.urlencode(query_parameters)})


@app.route('/oauth')
def oauth_handler():
    if 'error' in request.args and request.args.get('error') == 'access_denied':
        session.clear()
    elif 'code' in request.args:
        access_token = get_access_token(request.args.get('code'))
        user = Users.objects(username = session['username']).first()
        user.access_token = access_token
        user.save()

    return redirect(url_for('render_index'))


@app.route('/addNewProduct', methods=['POST'])
def add_new_product():
    product_data = request.get_json(force=True)

    interval = get_time_in_seconds(int(product_data['interval']), product_data['intervalUnit'])
    valid_asin, message = is_asin_valid(product_data['asin'])
    if not valid_asin:
        status = False
        return jsonify({'status' : status, 'message': message})

    valid_interval, message = is_interval_valid(interval)
    if not valid_interval:
        status = False
        return jsonify({'status' : status, 'message' : message})

    job = JobHandler.objects(interval = interval).first()

    # job_id = str(uuid.uuid4())
    #
    # product = Products(
    #     asin = product_data['asin'],
    #     interval = interval,
    #     threshold_price = int(product_data['thresholdPrice']),
    #     username = session['username'],
    #     job_id = job_id
    # )
    #
    # product.save()
    #
    # add_job_to_schedular(
    #     job = check_product_price_on_regular_interval,
    #     interval = get_time_in_seconds(int(product_data['interval']), product_data['intervalUnit']),
    #     job_id = job_id,
    #     args = [product_data['asin'], int(product_data['thresholdPrice'])]
    # )

    status = True
    message = 'Success ! Product added successfully.'

    return jsonify({'status' : status, 'message' : message})