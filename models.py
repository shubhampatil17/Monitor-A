from mongoengine import Document, StringField, EmailField, IntField

class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    access_token = StringField()


class Product(Document):
    asin = StringField(required=True)
    interval = IntField(required=True)
    threshold_price = IntField(required=True)
    last_notified_price = IntField()
    username = StringField(required=True)
    job_id = StringField(required=True)

