from django.urls import path
from .views import *


urlpatterns = [
    path('register/', CreateUser.as_view()),
    path('login/', Login.as_view()),
    # path('logout/', Logoutview.as_view()),
    path('vendors_list/', VendorsList.as_view()),
    path('fetch_tea_price/', FetchTeaPrice.as_view()),
    path('post_transaction/', PostTransaction.as_view()),
]
