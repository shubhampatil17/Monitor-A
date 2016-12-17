from services.database import DatabaseService
from services.mailer import MailerService

db_service = DatabaseService()
mailer = MailerService()

def check_product(asin, threshold_price):
    for product in db_service.find_products(asin=asin):
        #fetch product data
        current_price = 0.0
        if current_price != product.last_notified_price and current_price < threshold_price:
            mailer.send_mail()


