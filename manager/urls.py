from . import views
from django.urls import path

urlpatterns = [
    path('add_bookmark/', views.update_add_bookmark, name='add_bookmark'),
    path('add_favourite/', views.update_add_favourite, name='add_favourite'),
    path('remove_bookmark/', views.update_remove_bookmark, name='remove_bookmark'),
    path('remove_favourite/', views.update_remove_favourite, name='remove_favourite'),
    path('get_favourite/', views.update_get_favourite, name="get_favourite"),
    path('get_bookmark/', views.update_get_bookmark, name="get_bookmark")
]