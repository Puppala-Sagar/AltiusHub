from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.DATABASES['default']['CLIENT']['host'])
db = client[settings.DATABASES['default']['NAME']]

products_collection = db["items"]
users_collection = db['users']