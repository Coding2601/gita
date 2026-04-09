from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .no_sql_model import db, build_document

@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            uid = data.get('uid')
            email = data.get('email')
            if not uid:
                return JsonResponse({'message': 'uid is required'}, status=400)
            if db.user.find_one({ 'uid': data['uid'] }) is None:
                obj = {'uid': data['uid'], 'email': data['email']}
                doc = build_document(obj)
                db.user.insert_one(doc)
            else:
                obj = db.user.find_one({ 'uid': data['uid'] })
            res = JsonResponse({'message': 'success'}, status=200)
            res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
            return res
        except Exception as e:
            print(e)
            res = JsonResponse({'message': 'Failed to login'}, status=400)
            res['Access-Control-Allow-Origin'] = 'https://bhagavad-gita.netlify.app'
            return res