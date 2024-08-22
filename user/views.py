import datetime
import json
from django.shortcuts import render
import pytz
import hashlib
import random
import string
import uuid
import jwt
import secrets
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from user.models import User
from user.serializers import UserSerializer    
from .index import update_verified
#from . import utils
from .no_sql_model import db, build_document
from comman.check import protected

def salt():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def generate_secret_key():
    return secrets.token_hex(32)

def encrypt_password(password):
    hash_func = hashlib.sha256()
    saltVal = str(salt())
    hash_func.update((str(password)).encode('utf-8'))
    encrypt_password = hash_func.hexdigest()
    return encrypt_password, saltVal

def get_request_body(request):
    try:
        data = json.loads(request.body)
    except:
        data = request.POST
    return data

@csrf_exempt
def register(request):
    if request.method == 'POST':

        data = get_request_body(request)

        try:
            emailId = data['email']
            password, saltVal = encrypt_password(data['password'])
            username = emailId.split('@')[0]
            email_token = str(uuid.uuid4())

            password = password + '$' + saltVal

            obj = {'username': username, 'email': emailId, 'password': password, 'email_token': email_token, 'salt': saltVal}

            #utils.send_email_token(obj, email_token)

            serializer = UserSerializer(data=obj)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            doc = build_document(serializer.data)

            db.user.insert_one(doc)

            res = JsonResponse({'message': 'success', 'data': serializer.data}, status=200)
            res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
            return res
        except Exception as e:
            print(e)
            res = JsonResponse({'message': 'Failed to Register'}, status=400)
            res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
            return res
    
def verify(request, token):
    try:
        user = User.objects.get(email_token=token)
        update_verified(email_token=token)
        return render(request, './verified.html')
    except Exception as e:
        print(e)
        return render(request, './invalid.html')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = get_request_body(request)
        email = data['email']
        password, saltVal = encrypt_password(data['password'])
        user = User.objects.filter(email=email).first()
        
        if user is None:
            return JsonResponse({'message': 'User not found'})
        
        user_password = user.password.split('$')[0]

        if not (password == user_password):
            return JsonResponse({'message': 'Invalid Password'})
        
        '''if not user.is_verified:
            return JsonResponse({'message': 'Email not verified'}, status=400)'''
        
        curr_time, ist_timezone = datetime.datetime.utcnow(), pytz.timezone('Asia/Kolkata')
        ist_now = curr_time.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

        payload = {
            'username': user.username,
            'exp': ist_now + datetime.timedelta(days=0, minutes=60),
            'iat': ist_now
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = JsonResponse({'message': 'success'}, status=200)
        response.set_cookie(key='jwt', value=token, httponly=True, secure=True, samesite='Strict')
        print(token)
        return response

def logout(request):
    try:
        response = JsonResponse({'message': 'success'})
        response.delete_cookie('jwt', samesite='Strict')
        print(request.COOKIES)
        return response
    except Exception as e:
        print(e)
        res = JsonResponse({'message': 'Failed to logout'})
        res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
        return res

def protection(request):
    if request.method == 'GET':
        try:
            print(request.COOKIES)
            token = request.COOKIES.get('jwt')
            obj = protected(token)
            res = JsonResponse({'decoded': obj['decoded'], 'message': obj['message']})
            return res
        except Exception as e:
            print(e)
            res = JsonResponse({'message': 'Invalid Token'})
            return res
