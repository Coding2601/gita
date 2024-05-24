import urllib.parse
from django.http import JsonResponse
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from marshmallow import Schema, fields

key = urllib.parse.quote_plus('Shiv@123')
uri = f"mongodb+srv://shivam:{key}@cluster0.ar9ltk6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'), connect=False)

try:
    db = client.get_database('bhagavad-gita')
    print("Connected to the database")
except:
    print("Failed to connect to the database")

class NoSQLUser(Schema):
    id = fields.Int()
    username = fields.Str()
    email = fields.Email(required=True, unique=True)
    password = fields.Str()
    email_token = fields.Str()
    salt = fields.Str()
    is_verified = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

    class Meta:
        fields = ('id', 'username', 'email', 'password', 'email_token', 'salt', 'is_verified', 'created_at', 'updated_at')

def build_document(data):
    try:
        schema = NoSQLUser()
        res = schema.load(data)
        res['bookmarks'] = []
        res['favourites'] = []
        return res
    except Exception as e:
        print(e)
        return None
    
def get_document(username):
    try:
        user = db.user.find_one({'username': username})
        del user['_id']
        return user
    except Exception as e:
        print(e)
        return None
    
def delete_document(username):
    try:
        user = db.user.delete_one({'username': username})
    except Exception as e:
        print(e)
        return None
    
def update_document_verified(email_token):
    try:
        user = db.user.update_one({'email_token': email_token}, {'$set': {'is_verified': True}})
        return 'Successfully Updated'
    except Exception as e:  
        print(e)
        return None
    
def add_bookmark(username, data):
    try:
        curr_user = db.user.update_one({'username': username}, {'$addToSet': {'bookmarks': str(data)}})
        return 'Successfully Updated'
    except Exception as e:
        return e

def add_favourite(username, data):
    try:
        curr_user = db.user.update_one({'username': username}, {'$addToSet': {'favourites': str(data)}})
        return 'Successfully Updated'
    except Exception as e:
        return e
    
def remove_bookmark(username, data):
    try:
        curr_user = db.user.update_one({'username': username}, {'$pull': {'bookmarks': str(data)}})
        return 'Successfully Updated'
    except Exception as e: 
        return e

def remove_favourite(username, data):
    try:
        curr_user = db.user.update_one({'username': username}, {'$pull': {'favourites': str(data)}})
        return 'Successfully Removed'
    except Exception as e:
        return e
    
def get_favourites(username):
    try:
        curr_user = db.user.find_one({'username': username})
        del curr_user['_id']
        return curr_user
    except Exception as e:
        return e
    
def get_bookmarks(username):
    try:
        curr_user = db.user.find_one({'username': username})
        del curr_user['_id']
        return curr_user
    except Exception as e:
        return e