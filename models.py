from mongoengine import Document, StringField, EmailField, IntField, ListField

class Users(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    pn_access_token = StringField()


class Products(Document):
    asin = StringField(required=True)
    interval = IntField(required=True)
    threshold_price = IntField(required=True)
    last_notified_price = IntField()
    username = StringField(required=True)


class JobHandler(Document):
    interval = IntField(required=True, unique=True)
    job_id = StringField(required=True)
    asins = ListField(required=True)