from flask import Flask, redirect, render_template, url_for, request
from services.database import DatabaseService
# from services.schedular import SchedularService
import uuid

app = Flask(__name__)
db_service = DatabaseService('test')

# schedular_service = SchedularService()
# schedular_service.start_schedular()

@app.route("/")
def render_login_page():
    return render_template("login.html", loginFailed = False)

@app.route("/login", methods = ["POST"])
def check_credentials():
    username, password = request.form['username'], request.form['password']

    if(username == "dbrock" and password == "dbrock"):
        return redirect(url_for("render_homepage"))
    else:
        return render_template("login.html", loginFailed = True)


@app.route("/homepage")
def render_homepage():
    return render_template("homepage.html")

@app.route("/logout")
def logout_user():
    #clear session
    return redirect(url_for("render_login_page"))

@app.route("/addProduct", methods = ["POST"])
def add_product_to_monitor():
    asin = request.json['productASIN']
    interval = float(request.json['interval'])
    interval_unit = request.json['intervalUnit']
    threshold_price = float(request.json['thresholdPrice'])

    valid, err = db_service.is_valid_interval(interval, interval_unit)

    if valid:
        try:
            # job_id = uuid.uuid4()
            # db_service.save_product(asin, interval, interval_unit, threshold_price, 0.0, job_id)
            raise Exception("Hurray Exception")
            # if interval_unit == 'Weeks':
            #     schedular_service.add_job_to_schedular_store(job_id, asin, threshold_price, weeks=interval)
            # elif interval_unit == 'Days':
            #     schedular_service.add_job_to_schedular_store(job_id, asin, threshold_price, days=interval)
            # elif interval_unit == 'Hours':
            #     schedular_service.add_job_to_schedular_store(job_id, asin, threshold_price, hours=interval)
            # elif interval_unit == 'Minutes':
            #     schedular_service.add_job_to_schedular_store(job_id, asin, threshold_price, minutes=interval)
            # elif interval_unit == 'Seconds':
            #     schedular_service.add_job_to_schedular_store(job_id, asin, threshold_price, seconds=interval)

        except:
            pass

    else:
        return err

    return "Success"


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug= True)
