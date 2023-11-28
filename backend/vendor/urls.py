from django.urls import path
from .views import *


urlpatterns = [
    path('register/', CreateUser.as_view()),
    path('login/', Login.as_view()),
    # path('logout/', Logoutview.as_view()),
    path('create_tea_description/', CreateTeaDescription.as_view()),
    path('get_tea_description/', GetTeaDescription.as_view()),
    path('update_tea_description/', UpdateTeaDescription.as_view()),

]
