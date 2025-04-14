from django.shortcuts import render, get_object_or_404
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
from .models import DataStore, LeadgenData, TokenDate,UserData, UserLeadInfo
import urllib.parse

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
    

def get_valid_lead_fields():
    return {field.name for field in UserLeadInfo._meta.fields}

# Step 2: Parse the API response and clean data
def parse_field_data(field_data):
    data = {}
    for item in field_data:
        name = item.get("name")
        values = item.get("values")
        if name and values:
            data[name] = values[0]  # Take the first value from list
    return data

# Step 3: Save lead info using kwargs
def save_lead_info_from_response(response, user_uuid):
    field_data = response.get("field_data", [])
    print("fields_data",field_data)
    data = parse_field_data(field_data)
    print("data",data)

    # Ensure only valid model fields are included
    valid_fields = get_valid_lead_fields()
    print("valid_fields",valid_fields)
    cleaned_data = {k: v for k, v in data.items() if k in valid_fields}
    print("cleaned_data",cleaned_data)
    # Add required foreign key
    cleaned_data["user_uuid"] = user_uuid
    user_instance = UserData.objects.get(uuid=user_uuid)

    # Update cleaned_data to contain the instance instead of UUID
    cleaned_data["user_uuid"] = user_instance
    # Save the object
    lead = UserLeadInfo.objects.create(**cleaned_data)
    return True
# VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "your_custom_verify_token")
VERIFY_TOKEN = 'a2c75548ce868a44d4ed57164be29362054e0b4f83e135ad3c67b27319456498'  # Replace with your actual verify token


@csrf_exempt
def facebook_webhook(request,user_uuid):
    print("here")
    print("user_uuid",user_uuid)
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
            lead_data = lead_to_data(request,lead_id,user_uuid)
            print("lead_data",lead_data)
            save_lead_info_from_response(lead_data, user_uuid)
            print("save_lead_info_from_response",save_lead_info_from_response)
            user_instance = get_object_or_404(UserData, uuid=user_uuid)
            user_instance = UserData.objects.filter(uuid=user_uuid).first()
            print("user_instance",user_instance)
            # lead_instance = LeadgenData.objects.create(lead_id=lead_id,user_uuid=user_instance, lead_data=lead_data.get('field_data'))
            # print("lead_instance",lead_instance)

            return JsonResponse({"status": "received",
                                "id": data_instance.id}, status=200)
        except json.JSONDecodeError:
            print("error")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"error": "Server error", "details": str(e)}, status=500)

def fetch_lead_data(lead_id,long_access_token):
    url = f"https://graph.facebook.com/v22.0/{lead_id}?access_token={long_access_token}"
    response = requests.get(url)
    response_json = response.json()
    print("fetch_lead_data_response",response_json)
    return response_json


def lead_to_data(request,lead_id,user_uuid):
    long_token = TokenDate.objects.filter(user_uuid=user_uuid).first()
    # long_access_token = long_token.long_time_access_token
    print("long_access_token",long_token)
    if not long_token or not long_token.long_time_access_token:        
        print("in if")
        facebook_login_redirect(request,user_uuid )

        long_token = get_object_or_404(TokenDate, user_uuid=user_uuid)
        print("long_token_1",long_token)
        long_access_token = long_token.long_time_access_token
        print("long_access_token",long_access_token)
        reponse_data = fetch_lead_data(lead_id,long_access_token)
        return reponse_data
    l_t = long_token.long_time_access_token
    response_data = fetch_lead_data(lead_id,l_t)
    print("resonse_json",response_data)
    return response_data
    
def facebook_login_redirect(request,user_uuid):
    redirect_url = request.GET.get('redirect_url')
    print("redirect_url",redirect_url, user_uuid)
    user_data = UserData.objects.filter(uuid=user_uuid).first()
    app_id = user_data.app_id
    full_redirect_uri = f"{redirect_url}{user_uuid}/"
    base_url = "https://www.facebook.com/v18.0/dialog/oauth"
    params = {
        "client_id": app_id,
        "redirect_uri": full_redirect_uri,
        "scope": "pages_show_list,leads_retrieval,pages_read_engagement",
        "response_type": "token",
        "state": str(user_uuid),
    }
    facebook_url = f"{base_url}?{urlencode(params)}"
    decode_url = urllib.parse.unquote(facebook_url)
    print("decode",decode_url)
    return JsonResponse({"url": decode_url})



def facebook_callback(request,user_uuid):
    print("facebook_callback")
    code = request.GET.get("code")
    print("code")
    print(code)
    # user_uuid = request.GET.get("state")
    print("user", user_uuid)
    return render(request, "facebook_callback.html", {"user_uuid":user_uuid})


@csrf_exempt
def receive_token(request,user_uuid):
    print("=== receive_token hit ===")
    print("request",request)
    print("Request method:", request.method, "Request headers:", request.headers, "Request body:", request.body)
    user_data = UserData.objects.filter(uuid=user_uuid).first()
    print("user_data",user_data)
    app_id = user_data.app_id
    print("app_id", app_id)
    app_secret_key = user_data.app_secret_key
    print("app_secret_key", app_secret_key)
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        print("data", data)
        short_access_token = data.get("access_token")
        print("short_access_token", short_access_token)
        if short_access_token:
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
            # token_record = TokenDate.objects.get_or_create(user_uuid=user_uuid)
            user_instance = UserData.objects.get(uuid=user_uuid)

            token_record, created = TokenDate.objects.get_or_create(
                user_uuid=user_instance,
                defaults={
                    "short_time_access_token": short_access_token,
                    "long_time_access_token": long_access_token,
                    "short_token_created_date": now().date(),
                    "long_token_created_date": now().date(),
                }
            )

            if not created:
                token_record.short_time_access_token = short_access_token
                token_record.long_time_access_token = long_access_token
                token_record.short_token_created_date = now().date()
                token_record.long_token_created_date = now().date()
                token_record.save()

            return JsonResponse({"message": "success token save", "data": response_data_json})

        return JsonResponse({"error": "Access token missing"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




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