from django.urls import path
from . import views

urlpatterns = [
    path('callback', views.callback)    # 設定line bot響應網址
]