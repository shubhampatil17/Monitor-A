from mongoengine import Document, StringField, EmailField, IntField, FloatField, URLField


class Users(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    pn_access_token = StringField()


class Products(Document):
    asin = StringField(required=True, unique_with='username', max_length=10)
    interval = IntField(required=True)
    threshold_price = FloatField(required=True)
    username = StringField(required=True)
    locale = StringField(required=True)
    last_notified_price = FloatField(required=True)
    product_url = URLField()
    image_url = URLField()


class JobHandler(Document):
    interval = IntField(required=True, unique_with='locale')
    locale = StringField(required=True)
    job_id = StringField(required=True)
    batch_size = IntField(required=True)