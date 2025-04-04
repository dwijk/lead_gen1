from django.urls import path
from .views import HelloWorldView,facebook_webhook

urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello_world'),
    path('webhook/facebook/', facebook_webhook, name='facebook_webhook'),
]
