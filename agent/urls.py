from django.urls import path, include
from . import views

urlpatterns = [
    path('search/', views.semantic_search, name="semantic search"),
    path('chat/', views.chat, name="llm chat")
]