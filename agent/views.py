# Import Django utilities for handling HTTP responses and CSRF exemption
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import required libraries
import numpy as np
import os
import json
from dotenv import load_dotenv

# Import custom singleton classes for embedding, vector search, and LLM
from singleton.Embedder import EmbeddingModel
from singleton.VectorStore import VectorDB
from singleton.Cerebras import LLM

# Initialize embedding model using environment variable
embedder = EmbeddingModel(os.environ.get("EMBEDDING_MODEL"))

# Load vector database (FAISS index + metadata JSON)
vector_db = VectorDB('rag/gita_index.faiss', 'rag/gita_embeddings.json')

# Initialize LLM with model name from environment variable
llm = LLM(model_name=os.environ.get("MODEL_NAME"))


# ---------------------- SEMANTIC SEARCH API ----------------------
@csrf_exempt  # Disable CSRF protection (use carefully in production)
def semantic_search(request):
    # Allow only POST requests
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)
    
    try:
        # Parse incoming JSON request body
        body = json.loads(request.body)
        query = body.get("query")

        # Validate query input
        if not query:
            return JsonResponse({"message": "Query is required"}, status=400)

        # Convert query text into embedding vector
        query_vector = embedder.get_embedding(query).astype("float32")

        # Perform similarity search in vector DB (top 3 results)
        results = vector_db.search(query_vector, k=3)

        # Return only English slokas from results
        return JsonResponse({
            "query": query,
            "results": [result["eng_sloka"] for result in results]
        })

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({
            "message": "Semantic search failed",
            "error": str(e)
        }, status=500)


# ---------------------- CHAT API ----------------------
@csrf_exempt
def chat(request):
    # Allow only POST requests
    if request.method != "POST":
        return JsonResponse({"message": "Method not allowed"}, status=405)

    try:
        # Parse incoming JSON request body
        body = json.loads(request.body)
        prompt = body.get("prompt")
        temperature = body.get("temperature")

        # Validate prompt input
        if not prompt:
            return JsonResponse({"message": "prompt is required"}, status=400)

        # Convert user prompt into embedding vector
        query_vector = embedder.get_embedding(prompt).astype("float32")

        # Retrieve relevant verses as context from vector DB
        context = [result["verse"] for result in vector_db.search(query_vector, k=3)]

        # Generate response using LLM with context + system prompt
        response = llm.complete(
            user_prompt=prompt,
            context=context,
            temperature=temperature,
            system_prompt=(
                "You are Lord Krishna, explaining the teachings of the Bhagavad Gita "
                "in a simple, clear, and compassionate manner. Use the provided context "
                "to answer the user’s question. Always address the user by their name "
                "in your response. Respond in a natural, human-like way with warmth and empathy. "
                "Avoid robotic phrasing. Use conversational language, gentle guidance, and "
                "relatable analogies when helpful. Your tone should be calm, wise, and reassuring, "
                "like a trusted mentor speaking directly to the user."
            )
        )

        # Return generated response
        return JsonResponse({"message": str(response)}, status=200)

    except Exception as e:
        # Handle errors during chat processing
        return JsonResponse({
            "message": "Semantic search failed",
            "error": str(e)
        }, status=500)