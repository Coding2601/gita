from user.models import User
from django.http import JsonResponse
from .no_sql_model import get_document, delete_document, update_document_verified
#from user.serializers import UserSerializer
#from bson.json_util import dumps

def get(request, username):
    try:
        user = User.objects.filter(username=username).first()
        if user is None:
            return JsonResponse({'message': 'User not found'}, status=404)
        #serializer = UserSerializer(user)
        result = get_document(username)
        #print(dumps(result))
        return JsonResponse(result, status=200)
    except Exception as e:
        return JsonResponse({'message': e}, status=400)
    
def delete(request, username):
    try:
        user = User.objects.filter(username=username).first()
        if user is None:
            return JsonResponse({'message': 'User not found'}, status=404)
        user.delete()
        delete_document(username)
        return JsonResponse({'message': 'User deleted'}, status=200)
    except Exception as e:
        return JsonResponse({'message': e}, status=400)
    
def update_verified(email_token):
    try:
        user = User.objects.filter(email_token=email_token).first()
        if user is None:
            return JsonResponse({'message': 'User not found'}, status=404)
        user.is_verified = True
        user.save()
        update_document_verified(email_token)
    except:
        return JsonResponse({'message': 'Failed to update'}, status=400)