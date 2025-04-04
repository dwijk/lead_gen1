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
    context = {
        'users': users,
        'data_store': data_store,
        'lead_data':lead_data
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
    PAGE_ACCESS_TOKEN = "EAAH9kwN6EEUBO9z4guZCgqjNLOQeCmYT0bV3CC8kJaf0kmOKgrvZB6tlVWzgZBW5t1l1ZA5K2InR7J0k32MM1CiSiUTzH7EDTY3tVoDscnn84ZBtQipIgfy0OC5q6Vkw32sdXcUCxhU0P6J0xdGWj46htnuONCFC1GIdZAT9tJOBZBJEmF04ZAZA4ZA7oNl7nqZAiZCwQ7ahZCq9D5R9nmqU30PnOnVN4L6oYAGoE"
    url = f"https://graph.facebook.com/v22.0/{lead_id}?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.get(url)
    response_json = response.json()
    return response_json
    
    
