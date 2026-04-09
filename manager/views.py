from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
#from user.models import User
#from user.serializers import UserSerializer    
from user.no_sql_model import add_bookmark, add_favourite, remove_bookmark, remove_favourite, get_favourites, get_bookmarks
from comman.check import protected
import json
from datetime import datetime
import os

curr_dir = "C:\\Users\\Ravi Mishra\\OneDrive\\Documents\\Projects\\gita-venv\\Scripts\\gita\\gita"

def get_request_body(request):
    try:
        data = json.loads(request.body)
    except Exception as e:
        print(e)
    return data

def getEngSloka(chpt_no, verse_no):
    chpt_no, verse_no = int(chpt_no), int(verse_no)
    try:
        with open(os.path.join(curr_dir, f"v2English/chapter {chpt_no}/{chpt_no}.{verse_no}.txt"), encoding="utf-8") as f:
            slok = f.read()
        return slok.replace("\n", "\n\n")
    except Exception as e:
        return str(e)

def getSansSloka(chpt_no, verse_no):
    chpt_no, verse_no = int(chpt_no), int(verse_no)
    try:
        with open(os.path.join(curr_dir, f"Sanskrit Slokas/chapter {chpt_no}/{chpt_no}.{verse_no}.txt"), encoding="utf-8") as f:
            slok = f.read()
        return slok.replace("\n", "\n\n")
    except Exception as e:
        return str(e)

def generate_response(data):
    ans = []
    for item in data:
        chpater, verse  = str(item).split('.')
        obj = {
            'chapter': int(chpater),
            'verse': int(verse),
            'verseLabel': item,
            'meaning': getEngSloka(chpater, verse),
            'sanskrit': getSansSloka(chpater, verse),
            'savedAt': datetime.now().isoformat()
        }
        ans.append(obj)
    return ans

@csrf_exempt
def update_add_bookmark(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        try:
            body = get_request_body(request)
            print(body)
            username = request.uid
            response = add_bookmark(username, body['data']['data'])
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
        username = request.uid
        body = get_request_body(request)
        response = add_favourite(username, body['data']['data'])
        res = JsonResponse({'message': response}, status=200)
        res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
        return res
    
@csrf_exempt
def update_remove_bookmark(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        username = request.uid
        body = get_request_body(request)
        response = remove_bookmark(username, body['data']['data'])
        print(response)
        res = JsonResponse({'message': response}, status=200)
        res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
        return res

@csrf_exempt
def update_remove_favourite(request):
    if request.method == 'POST':
        #username, body = decode_jwt(request), get_request_body(request)
        username = request.uid
        body = get_request_body(request)
        print(body)
        response = remove_favourite(username, body['data']['data'])
        res = JsonResponse({'message': response}, status=200)
        res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
        return res
    
def update_get_favourite(request):
    #username = 'shivamkmishra9'
    username = request.uid
    response = get_favourites(username)
    response = generate_response(response['favourites'])
    res = JsonResponse({'message': response}, status=200)
    res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
    return res

def update_get_bookmark(request):
    username = request.uid
    response = get_bookmarks(username)
    data = generate_response(response['bookmarks'])
    res = JsonResponse({'message': data}, status=200)        
    res['Access-Control-Allow-Origin'] = 'https://bhaagvad-gita.netlify.app'
    return res