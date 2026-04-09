from django.http import JsonResponse
from singleton.Firebase import FirebaseAuth

class AuthMiddleware:
    BLOCKED_PATHS = ('/user/login/', '/agent')
    def __init__(self, get_response):
        self.get_response = get_response
        self.firebase = FirebaseAuth()

    def __call__(self, request):
        if request.path.startswith(self.BLOCKED_PATHS):
            return self.get_response(request)
        token = request.headers.get("Authorization")
        if not token:
            return JsonResponse({"message": "Authorization header missing"}, status=401)
        if not token.startswith("Bearer "):
            return JsonResponse({"message": "Invalid authorization format"}, status=401)
        token = token.split(" ")[1]
        decoded = self.firebase.verify_token(token)
        if not decoded:
            return JsonResponse({"message": "Invalid or expired token"}, status=401)
        request.uid = decoded.get('uid')
        response = self.get_response(request)
        return response