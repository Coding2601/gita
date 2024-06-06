from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
#from user.models import User
#from user.serializers import UserSerializer    
from user.no_sql_model import add_bookmark, add_favourite, remove_bookmark, remove_favourite, get_favourites, get_bookmarks
from comman.check import protected
import json

def get_request_body(request):
    try:
        data = json.loads(request.body)
    except Exception as e:
        print(e)
    return data

@csrf_exempt
def update_add_bookmark(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        try:
            body = get_request_body(request)
            print(body)
            #username = 'shivamkmishra9'
            response = add_bookmark(body['data']['username'], body['data']['data'])
            res = JsonResponse({'message': response}, status=200)
            res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
            return res
        except Exception as e:
            print(e)
            return None

@csrf_exempt
def update_add_favourite(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        #username = 'shivamkmishra9'
        body = get_request_body(request)
        print(body)
        response = add_favourite(body['data']['username'], body['data']['data'])
        res = JsonResponse({'message': response}, status=200)
        res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
        return res
    
@csrf_exempt
def update_remove_bookmark(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        #username = 'shivamkmishra9'
        body = get_request_body(request)
        print(body)
        response = remove_bookmark(body['data']['username'], body['data']['data'])
        print(response)
        res = JsonResponse({'message': response}, status=200)
        res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
        return res

@csrf_exempt
def update_remove_favourite(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        #username = 'shivamkmishra9'
        body = get_request_body(request)
        print(body)
        response = remove_favourite(body['data']['username'], body['data']['data'])
        res = JsonResponse({'message': response}, status=200)
        res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
        return res
    
def update_get_favourite(request, username):
    #username = 'shivamkmishra9'
    response = get_favourites(username)
    res = JsonResponse(response, status=200)
    res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
    return res

def update_get_bookmark(request, username):
    #username = 'shivamkmishra9'
    response = get_bookmarks(username)
    print(response)
    res = JsonResponse(response, status=200)        
    res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
    return res