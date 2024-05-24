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
            #username = 'shivamkmishra9'
            response = add_bookmark(body['username'], body['data'])
            return JsonResponse({'message': response}, status=200)
        except Exception as e:
            print(e)
            return None

@csrf_exempt
def update_add_favourite(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        #username = 'shivamkmishra9'
        body = get_request_body(request)
        response = add_favourite(body['username'], body['data'])
        return JsonResponse({'message': response}, status=200)
    
@csrf_exempt
def update_remove_bookmark(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        #username = 'shivamkmishra9'
        body = get_request_body(request)
        response = remove_bookmark(body['username'], body['data'])
        print(response)
        return JsonResponse({'message': response}, status=200)

@csrf_exempt
def update_remove_favourite(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        #username = 'shivamkmishra9'
        body = get_request_body(request)
        response = remove_favourite(body['username'], body['data'])
        print(response)
        return JsonResponse({'message': response}, status=200)
    
def update_get_favourite(request, username):
    #username = 'shivamkmishra9'
    response = get_favourites(username)
    return JsonResponse(response, status=200)

def update_get_bookmark(request, username):
    #username = 'shivamkmishra9'
    response = get_bookmarks(username)
    print(response)
    return JsonResponse(response, status=200)        