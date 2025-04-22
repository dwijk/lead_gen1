from django.urls import path
from .views import HelloWorldView,facebook_webhook, facebook_callback,receive_token, facebook_login_redirect, fetch_data, google_ads_webhook

urlpatterns = [
    path('hello/', HelloWorldView.as_view(), name='hello_world'),
    path('webhook/facebook/<uuid:user_uuid>/', facebook_webhook, name='facebook_webhook'),
    
    # redirect url then call for access token
    path('auth/facebook/callback/<uuid:user_uuid>/', facebook_callback, name='facebook_callback'),
    
    # after redirect this url hit
    path('auth/facebook/receive-token/<uuid:user_uuid>/', receive_token, name='receive_token'),
    path('facebook/login/<uuid:user_uuid>/', facebook_login_redirect, name='facebook-login'),  # First time 
    path('fetch-data/<uuid:user_uuid>/', fetch_data, name='fetch_data'),
    path('google-ads-webhook/', google_ads_webhook, name='google_ads_webhook'),

]
