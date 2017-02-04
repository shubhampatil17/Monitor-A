from mongoengine import Document, StringField, EmailField, IntField

class Users(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    pn_access_token = StringField()


class Products(Document):
    asin = StringField(required=True, unique_with='username')
    interval = IntField(required=True)
    threshold_price = IntField(required=True)
    last_notified_price = IntField()
    username = StringField(required=True)
    locale = StringField(required=True)


class JobHandler(Document):
    interval = IntField(required=True, unique_with='locale')
    locale = StringField(required=True)
    job_id = StringField(required=True)
    batch_size = IntField(required=True)