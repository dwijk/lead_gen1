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
import requests
from .models import DataStore, LeadgenData
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
def facebook_webhook(request):
    print("here")
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
            lead_instance = LeadgenData.objects.create(lead_id=lead_id, lead_data=lead_data.get('field_data'))
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
    
    
def facebook_callback(request):
    print("facebook_callback")
    return render(request, "facebook_callback.html")


@csrf_exempt
def receive_token(request):
    print("=== receive_token hit ===")
    print("Request method:", request.method)
    print("Request headers:", request.headers)
    print("Request body:", request.body)
    if request.method == "POST":
        data = json.loads(request.body)
        access_token = data.get("access_token")

        if access_token:
            request.session["fb_access_token"] = access_token
            return JsonResponse({"message": "Token saved", "access_token": access_token})

        return JsonResponse({"error": "Access token missing"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)