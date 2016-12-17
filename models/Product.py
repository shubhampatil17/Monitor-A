from mongoengine import Document
from mongoengine import StringField, IntField, FloatField, UUIDField

class Product(Document):
    asin = StringField(required = True)
    interval = IntField()
    interval_unit = StringField()
    threshold_price = FloatField()
    last_notified_price = FloatField()
    job_id = UUIDField()