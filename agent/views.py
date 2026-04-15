# Import Django utilities for handling HTTP responses and CSRF exemption
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import required libraries
import os
import json
import requests

# External service configuration from environment variables
EXTERNAL_SERVICE_URL = os.environ.get("EXTERNAL_SERVICE_URL", "http://localhost:8001")


def _get_headers():
    """Build headers for external service requests."""
    return {"Content-Type": "application/json"}


# ---------------------- SEMANTIC SEARCH API ----------------------
@csrf_exempt
def semantic_search(request):
    """
    Proxy semantic search requests to external service.
    Expects JSON body: {"query": "user search query"}
    Returns: {"query": "...", "results": [...]}
    """
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
        query = body.get("query")

        if not query:
            return JsonResponse({"message": "Query is required"}, status=400)

        # Forward request to external semantic search endpoint
        response = requests.post(
            f"{EXTERNAL_SERVICE_URL}/search",
            headers=_get_headers(),
            json={"query": query, "k": body.get("k", 3)},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        return JsonResponse({
            "query": query,
            "results": data.get("results", [])
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "message": "Semantic search service unavailable",
            "error": str(e)
        }, status=503)
    except Exception as e:
        return JsonResponse({
            "message": "Semantic search failed",
            "error": str(e)
        }, status=500)


# ---------------------- CHAT API ----------------------
@csrf_exempt
def chat(request):
    """
    Proxy chat requests to external LLM service.
    Expects JSON body: {"prompt": "...", "temperature": 0.7, "user_name": "..."}
    Returns: {"message": "..."}
    """
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        body = json.loads(request.body)
        prompt = body.get("prompt")
        temperature = body.get("temperature", 0.7)
        user_name = body.get("user_name", "friend")

        if not prompt:
            return JsonResponse({"message": "prompt is required"}, status=400)

        system_prompt = (
            "You are Lord Krishna, explaining the teachings of the Bhagavad Gita "
            "in a simple, clear, and compassionate manner. Use the provided context "
            f"to answer the user's question. Always address the user by their name ({user_name}) "
            "in your response. Respond in a natural, human-like way with warmth and empathy. "
            "Avoid robotic phrasing. Use conversational language, gentle guidance, and "
            "relatable analogies when helpful. Your tone should be calm, wise, and reassuring, "
            "like a trusted mentor speaking directly to the user."
        )

        # Forward request to external chat/completion endpoint
        response = requests.post(
            f"{EXTERNAL_SERVICE_URL}/chat",
            headers=_get_headers(),
            json={
                "prompt": prompt,
                "temperature": temperature,
                "system_prompt": system_prompt,
                "context_k": body.get("context_k", 3)
            },
            timeout=60
        )
        response.raise_for_status()
        data = response.json()

        return JsonResponse({"message": data.get("response", data.get("message", ""))}, status=200)

    except requests.exceptions.RequestException as e:
        return JsonResponse({
            "message": "Chat service unavailable",
            "error": str(e)
        }, status=503)
    except Exception as e:
        return JsonResponse({
            "message": "Chat processing failed",
            "error": str(e)
        }, status=500)
