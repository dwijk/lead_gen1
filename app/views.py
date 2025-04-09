from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import  User
# from dotenv import load_dotenv
import json
import os
from django.utils.timezone import now
import requests
from urllib.parse import urlencode
from django.shortcuts import redirect
from .models import DataStore, LeadgenData, TokenDate,UserData
# load_dotenv()
        

def home(request):
    users = User.objects.all()  # Fetch all users
    data_store = DataStore.objects.all()  # Fetch all DataStore entries
    lead_data = LeadgenData.objects.all()
    access_token = request.session.get('fb_access_token', None)

    context = {
        'users': users,
        'data_store': data_store,
        'lead_data':lead_data,
        'access_token':access_token
    }
    
    return render(request, 'home.html', context)


class HelloWorldView(APIView):
    def get(self, request):
        print("hello dwij")
        return Response({"message": "Hello World"}, status=status.HTTP_200_OK)
    


# VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "your_custom_verify_token")
VERIFY_TOKEN = 'a2c75548ce868a44d4ed57164be29362054e0b4f83e135ad3c67b27319456498'  # Replace with your actual verify token


@csrf_exempt
def facebook_webhook(request,user_uuid):
    print("here")
    user_uuid = request.GET.get("uuid")
    print("uuid",user_uuid)
    if request.method == "GET":

        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge)
        else:
            return JsonResponse({"error": "Invalid verification token"}, status=403)
    elif request.method == "POST":
        # Handle the webhook event
        print("post")
        try:
            payload = json.loads(request.body)
            print("payload",payload)
            data_instance = DataStore.objects.create(name="Lead Data", data=payload)
            lead_id = payload.get('entry')[0].get('changes')[0].get('value').get('leadgen_id')
            print("lead_id",lead_id)
            lead_data = lead_to_data(lead_id)
            print("lead_data",lead_data)
            lead_instance = LeadgenData.objects.create(lead_id=lead_id,user_uuid=user_uuid, lead_data=lead_data.get('field_data'))
            return JsonResponse({"status": "received",
                                "id": data_instance.id}, status=200)
        except json.JSONDecodeError:
            print("error")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"error": "Server error", "details": str(e)}, status=500)


def lead_to_data(lead_id):
    PAGE_ACCESS_TOKEN = "EAAH9kwN6EEUBO8ZAb6e3jHrLnCwfYvU25yRu2SZCj41mjw06k3GUzuDxwUbmuKhZAouFG5pqB945ijPVsmGZCyjYUFqvEHQSvoQILMOoMdeGU1dZAXItJkMvwrm41EpTi1E9URoNwwofOaZCbCqKtAZAvdkguxeHJdB8ic3zSZCi4HC7AsTFVq8TkZCBw88fmCqwwH2Wo4k5peZAd38Y0ZAB0pXFJSDtQZDZD"
    url = f"https://graph.facebook.com/v22.0/{lead_id}?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.get(url)
    print("response",response)
    response_json = response.json()
    print("resonse_json",response_json)
    return response_json
    
    
def facebook_callback(request,user_uuid):
    print("facebook_callback")
    return render(request, "facebook_callback.html", {"user_uuid":user_uuid})


@csrf_exempt
def receive_token(request,user_uuid):
    print("=== receive_token hit ===")
    print("Request method:", request.method, "Request headers:", request.headers, "Request body:", request.body)
    # token_data = TokenDate.objects.filter(user_uuid=user_uuid).first()
    # print("token_data", token_data)
    # access_token = token_data.long_time_access_token
    # print("access", access_token)
    user_data = UserData.objects.filter(user_uuid=user_uuid).first()
    app_id = user_data.app_id
    app_secret_key = user_data.app_secret_key
    if request.method == "POST":
        data = json.loads(request.body)
        # short_access_token = data.get("access_token")
        short_access_token = "560282837061701|FAtCDEtvlVCZa3n_OdRYzOf376Y"
        print("short_access_token", short_access_token)
        if short_access_token:
            
            # token_valid_url = "https://graph.facebook.com/debug_token"
            # token_info_params = {
                
            #     "input_token":access_token,
            #     "access_token":f"{app_id}|{app_secret_key}"  # app_id|app_secret_key
            # }
            # response_token_valid = requests.get(token_valid_url, params=token_info_params)
            # response_token_valid_json = response_token_valid.json()
            # print("resposnse_token_valid_json",response_token_valid_json)
            # print("is_valid",response_token_valid_json.get('data').get('is_valid'))
            # if not response_token_valid_json.get('data').get('is_valid'):
            request.session["fb_access_token"] = short_access_token
            long_term_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "client_id": app_id,
                "client_secret": app_secret_key,
                "fb_exchange_token": short_access_token,
                "grant_type": "fb_exchange_token"
            }

            response = requests.get(long_term_url, params=params)
            print("request2",request)
            data = response.json()
            print("data",data)
            long_access_token = data.get('access_token')
            print("long term access token", long_access_token)
            # add database store long term access token
            lead_data = "https://graph.facebook.com/v22.0/1301866194236291"
            params_data = {
                "access_token":long_access_token
            }
            response_data = requests.get(lead_data,params=params_data)
            print("response_data",response_data)
            response_data_json = response_data.json()
            print("lead data", response_data_json)
            token_record = TokenDate.objects.get_or_create(user_uuid=user_uuid)

            # Update tokens and dates
            token_record.short_time_access_token = short_access_token
            token_record.long_time_access_token = long_access_token
            token_record.short_token_created_date = now().date()
            token_record.long_token_created_date = now().date()
            token_record.save()
            return JsonResponse({"message": "success", "data": response_data_json})

        return JsonResponse({"error": "Access token missing"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def facebook_login_redirect(request,user_uuid):
    user_data = UserData.objects.filter(user_uuid=user_uuid).first()
    print("user data", user_data)
    app_id = user_data.app_id
    print("app_id", app_id)
    base_url = "https://www.facebook.com/v19.0/dialog/oauth"
    params = {
        "client_id": app_id,
        "redirect_uri": "https://lead-gen1.vercel.app/app/auth/facebook/callback/",
        "scope": "pages_show_list,leads_retrieval,pages_read_engagement",
        "response_type": "token"
    }
    facebook_url = f"{base_url}?{urlencode(params)}"
    return redirect(facebook_url)




def fetch_data(request, user_uuid):
    lead_data = "https://graph.facebook.com/v22.0/1301866194236291"
    # fetch access Token from uuid
    user_data = TokenDate.objects.filter(user_uuid=user_uuid).first()
    print("user data", user_data)
    access_token = user_data.long_time_access_token
    print("access", access_token)
    params_data = {
        "access_token":access_token         # access token
    }
    response_data = requests.get(lead_data,params=params_data)
    print("response_data",response_data)
    response_data_json = response_data.json()
    print("lead data", response_data_json)
    # Store data in DB
    return JsonResponse({"message": "success", "data": response_data_json})