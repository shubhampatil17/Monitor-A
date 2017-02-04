from flask import Flask, render_template, session, redirect, url_for, jsonify, request
import time
import json
import uuid
import urllib
from passlib.hash import pbkdf2_sha256
import database_connection
import api_endpoints
from models import Users, Products, JobHandler
from amazon_operations import is_asin_valid, is_interval_valid, check_product_price_on_regular_interval
from pushbullet_operations import check_current_user_data, get_access_token
from schedular_operations import schedular, add_job_to_schedular
from utils import get_time_in_seconds

app = Flask(__name__)
config = json.loads(open('config.json').read())


@app.route('/')
def render_index():
    return render_template('index.html')


@app.route('/checkLoginStatus')
def check_login_status():
    return jsonify(
        {'status': 'username' in session, 'username': session['username'] if 'username' in session else None})


@app.route('/login', methods=['POST'])
def check_login_credentials():
    credentials = request.get_json(force=True)
    try:
        if credentials['username'] and credentials['password']:
            valid_credentials = pbkdf2_sha256.verify(credentials['password'],
                                                     Users.objects(username=credentials['username']).first().password)
        else:
            valid_credentials = False
    except:
        valid_credentials = False

    if valid_credentials:
        session['username'] = credentials['username']

    return jsonify({'status': valid_credentials})


@app.route('/logout')
def logout_user():
    session.clear()
    return jsonify({'status': 'username' not in session})


@app.route('/checkAccessTokenValidity')
def check_access_token_validity():
    response = check_current_user_data(session['username'])
    return jsonify({'status': 'error' not in response})


@app.route('/checkUsernameValidity', methods=['POST'])
def check_username_validity():
    username = request.get_json(force=True)['username']
    users = Users.objects(username=username)
    return jsonify({'status': len(users) == 0})


@app.route('/checkEmailValidity', methods=['POST'])
def check_email_validity():
    email = request.get_json(force=True)['email']
    users = Users.objects(email=email)
    return jsonify({'status': len(users) == 0})


@app.route('/signUpUser', methods=['POST'])
def sign_up_user():
    signup_data = request.get_json(force=True);
    username = signup_data['username']
    email = signup_data['email']
    password = pbkdf2_sha256.hash(signup_data['password'])

    user = Users(username=username, email=email, password=password)
    user.save()
    return jsonify({'status': True})


@app.route('/getOAuthUrl')
def get_oauth_url():
    query_parameters = {
        'client_id': config['PUSHBULLET_CLIENT_ID'],
        'redirect_uri': 'https://www.monitora.ml/oauth',
        'response_type': 'code'
    }

    return jsonify({'status': True, 'oauth_url': api_endpoints.PUSHBULLET_OAUTH_ENDPOINT + "?" + urllib.parse.urlencode(
        query_parameters)})


@app.route('/oauth')
def oauth_handler():
    if 'error' in request.args and request.args.get('error') == 'access_denied':
        session.clear()
    elif 'code' in request.args:
        access_token = get_access_token(request.args.get('code'))
        user = Users.objects(username=session['username']).first()
        user.pn_access_token = access_token
        user.save()

    return redirect(url_for('render_index'))


@app.route('/addNewProduct', methods=['POST'])
def add_new_product():
    product_data = request.get_json(force=True)
    interval = get_time_in_seconds(int(product_data['interval']), product_data['intervalUnit'])

    valid_asin, message = is_asin_valid(product_data['asin'])
    if not valid_asin:
        status = False
        return jsonify({'status': status, 'message': message})

    valid_interval, message = is_interval_valid(interval, product_data['asin'], session['username'])
    if not valid_interval:
        status = False
        return jsonify({'status': status, 'message': message})

    existing_product = Products.objects(asin=product_data['asin'], username=session['username']).first()
    if existing_product:
        job = JobHandler.objects(interval=existing_product.interval, locale=existing_product.locale).first()
        job.batch_size -= 1
        if job.batch_size:
            job.save()
        else:
            schedular.remove_job(job_id=job.job_id)
            job.delete()

        existing_product.delete()

    product = Products(
        asin=product_data['asin'],
        interval=interval,
        threshold_price=int(product_data['thresholdPrice']),
        username=session['username'],
        locale=product_data['locale']
    )

    product.save()

    existing_job = JobHandler.objects(interval=interval, locale=product_data['locale']).first()
    if existing_job:
        existing_job.batch_size += 1
        existing_job.save()
    else:
        job = JobHandler(interval=interval, locale=product_data['locale'], job_id=str(uuid.uuid4()), batch_size=1)
        job.save()

        add_job_to_schedular(
            job=check_product_price_on_regular_interval,
            interval=interval,
            job_id=job.job_id,
            args=[interval, product_data['locale']]
        )

    status = True
    message = 'Success ! Product added successfully.'

    return jsonify({'status': status, 'message': message})


@app.route('/deleteProduct', methods=['DELETE'])
def delete_product():
    product_data = request.get_json(force=True)
    existing_product = Products.objects(asin=product_data['asin'], username=session['username']).first()

    if existing_product:
        job = JobHandler.objects(interval=existing_product.interval, locale=existing_product.locale).first()
        job.batch_size -= 1
        if job.batch_size:
            job.save()
        else:
            schedular.remove_job(job_id=job.job_id)
            job.delete()

        existing_product.delete()
        status = True
        message = 'Success ! Product deleted successfully.'
    else:
        status = False
        message = 'Error ! No such product found in database.'

    return jsonify({'status': status, 'message': message})


@app.route('/getRandomProducts', methods=['GET'])
def get_random_products():
    products = json.loads(Products.objects().to_json())
    products = products[:20] if len(products) > 20 else products
    return jsonify({'status': True, 'products': products})


@app.route('/getUserProducts', methods=['GET'])
def get_user_product():
    products = json.loads(Products.objects(username=session['username']).to_json())
    return jsonify({'status': True, 'products': products})
