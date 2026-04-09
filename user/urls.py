from . import views
from . import index
from . import login
from django.urls import path

urlpatterns = [
    path('register/', views.register, name='register'),
    # path('verify/<str:token>', views.verify, name='verify'),
    path('login/', login.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('get/<str:username>', index.get, name='get'),
    path('delete/<str:username>', index.delete, name='delete'),
    # path('protection/', views.protection, name='protection')
]