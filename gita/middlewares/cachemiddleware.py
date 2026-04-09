from django.http import JsonResponse
from singleton.Redis import RedisCache
import json
from dotenv import load_dotenv
import os

load_dotenv()

class CacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = RedisCache(url = os.environ.get("UPSTASH_REDIS_REST_URL"), token=os.environ.get("UPSTASH_REDIS_REST_TOKEN"))

    def __call__(self, request):
        if request.method == 'GET':
            if request.path.startswith("/getVerse"):
                cred = request.path.split("/")
                cache_key = f"verse:{cred[-2]}:{cred[-1]}"
                target_verse = self.cache.get(cache_key)
                if target_verse:
                    try:
                        print("Cache hit for key: ", cache_key)
                        data = json.loads(target_verse)
                        return JsonResponse(data, safe=False)
                    except Exception as e:
                        print("error occured-1: ", e)
                        pass
                response = self.get_response(request)
                if response.status_code == 200:
                    try:
                        data = json.loads(response.content.decode("utf-8"))
                        self.cache.set(cache_key, json.dumps(data), ttl=60)
                    except Exception as e:
                        print("error occured-2: ", e)
                        pass
                return response
        return self.get_response(request)