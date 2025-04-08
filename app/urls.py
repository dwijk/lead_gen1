from django.urls import path
from .views import HelloWorldView,facebook_webhook, facebook_callback,receive_token

urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello_world'),
    path('webhook/facebook/', facebook_webhook, name='facebook_webhook'),
    path('auth/facebook/callback/', facebook_callback, name='facebook_callback'),
    path('auth/facebook/receive-token/', receive_token, name='receive_token'),

]
