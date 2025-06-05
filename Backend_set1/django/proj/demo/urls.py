from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user),
    path('login/', views.login_user),
    path('products/', views.get_products),
    path('products/<str:id>/', views.update_product),
]

# pip install django pymongo bcrypt pyjwt python-dotenv

