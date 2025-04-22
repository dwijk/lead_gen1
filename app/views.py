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
from .models import DataStore, LeadgenData, TokenDate,UserData, UserLeadInfo, AdSet, Ad, Campaign, GeoLocation,Interest,Targeting,PromotedObject
import urllib.parse
from django.utils.dateparse import parse_datetime
from django.db.models import Prefetch

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
def formid_to_name(formid,long_access_token):
    url = f"https://graph.facebook.com/v22.0/{formid}?access_token={long_access_token}"
    response = requests.get(url)
    response_json = response.json()
    form_name = response_json.get("name")
    return form_name



def save_lead_info_from_response(response, user_uuid,lead_id,ad_id, form_id, long_access_token):
    field_data = response.get("field_data", [])
    print("fields_data",field_data)
    data = parse_field_data(field_data)
    print("data",data)

    # Ensure only valid model fields are included
    valid_fields = get_valid_lead_fields()
    print("valid_fields",valid_fields)
    cleaned_data = {k: v for k, v in data.items() if k in valid_fields}
    print("cleaned_data",cleaned_data)
    if not cleaned_data:
        print("False")
        return False
    # Add required foreign key
    cleaned_data["user_uuid"] = user_uuid
    user_instance = UserData.objects.get(uuid=user_uuid)
    lead_data = LeadgenData.objects.filter(lead_id=lead_id).first()
    # Update cleaned_data to contain the instance instead of UUID
    cleaned_data["user_uuid"] = user_instance
    cleaned_data["lead_id"] = lead_data.lead_id
    cleaned_data["ad_id"] = ad_id
    form_name = formid_to_name(form_id,long_access_token)
    cleaned_data["form_name"] = form_name
    print("cleaned_data2",cleaned_data)
    # Save the object
    lead = UserLeadInfo.objects.create(**cleaned_data)
    return True

def adset_to_campaign(adset_id, long_access_token, user_instance):
    print("adset_to_campaign")
    url = f"https://graph.facebook.com/v22.0/{adset_id}?fields=campaign_id&access_token={long_access_token}"
    # response = requests.get(url)
    # response_json = response.json()
    response_json = {
    "campaign_id": "44122334455667788",
    "id": "441234567890123456"
    }

    campaign_id = response_json.get('campaign_id')
    campaign = Campaign.objects.filter(campaign_id=campaign_id).first()
    if campaign:
        return campaign
    # campaign URL
    print("in if campaign_data")
    campaign_url = f"https://graph.facebook.com/v22.0/{campaign_id}?fields=id,name,status,budget_remaining,objective,start_time,stop_time,daily_budget,lifetime_budget&access_token={long_access_token}"
    # campaign_response = requests.get(campaign_url)
    # campaign_data = campaign_response.json()
    campaign_data = {
        "id": "44122334455667788",
        "name": "My Campaign",
        "status": "ACTIVE",
        "budget_remaining": "1000000",
        "objective": "LEAD_GENERATION",
        "start_time": "2025-04-01T00:00:00+0000",
        "stop_time": "2025-04-30T23:59:59+0000",
        "daily_budget": "50000",
        "lifetime_budget": "1500000"
        }

    # Extract data with safe defaults
    campaign = Campaign.objects.create(
    user_uuid=user_instance,
    campaign_id=campaign_id,
    name=campaign_data.get("name"),
    effective_status=campaign_data.get("status"),
    budget_remaining=campaign_data.get("budget_remaining", 0),
    objective=campaign_data.get("objective"),
    start_time=parse_datetime(campaign_data.get("start_time")),
    end_time=parse_datetime(campaign_data.get("stop_time")),
    daily_budget=campaign_data.get("daily_budget", 0),
    lifetime_budget=campaign_data.get("lifetime_budget", 0)
    )
    print("campaign",campaign)
    return campaign
    
def adid_to_adset(ad_id, long_access_token, user_instance):
    print("adid_to_adset")
    url = f"https://graph.facebook.com/v22.0/{ad_id}?fields=adset_id&access_token={long_access_token}"
    # response = requests.get(url)
    # response_json = response.json()
    response_json = {
        "adset_id": "1245678901",
        "id": "44987654321098765"
        }       
    adset_id = response_json.get('adset_id')

    # check_adset_id = AdSet.objects.filter(ad_set_id=adset_id).first()
    # adset = AdSet.objects.select_related(
    #     'targeting', 'promoted_object', 'campaign_id'
    # ).prefetch_related(
    #     Prefetch('targeting__geo_locations'),
    #     Prefetch('targeting__interests')
    # ).filter(adset_id=adset_id).first()
    adset = AdSet.objects.select_related(
        'targeting', 'promoted_object', 'campaign_id'
    ).prefetch_related(
        Prefetch('targeting__geo_locations'),
        Prefetch('targeting__interests')
    ).filter(adset_id=adset_id).first()
    print("adset",adset)
    if adset:
        print("in if adset")
        return adset

    # Step 3: If not found, fetch and create AdSet
    campaign = adset_to_campaign(adset_id, long_access_token, user_instance)
    print("campiagn",campaign)
    data = {
        "id": "1245678901",
        "name": "Ad Set 1",
        "campaign_id": "44122334455667788",
        "account_id": "act_441234567890",
        "status": "ACTIVE",
        "daily_budget": "10000",
        "lifetime_budget": "500000",
        "budget_remaining": "450000",
        "bid_amount": 200,
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LEAD_GENERATION",
        "start_time": "2025-04-10T00:00:00+0000",
        "end_time": "2025-04-30T23:59:00+0000",
        "destination_type": "WEBSITE",
        "targeting": {
            "age_min": 25,
            "age_max": 45,
            "genders": [1],
            "geo_locations": {"countries": ["US"]},
            "interests": [
                {"id": "4416003139266461", "name": "Technology"},
                {"id": "446003337891234", "name": "Startups"}
            ]
        },
        "promoted_object": {
            "page_id": "44123456789012345",
            "custom_event_type": "LEAD"
        }
    }

    # Step 4: Create Targeting
    targeting = None
    targeting_data = data.get("targeting")
    if targeting_data:
        geo_objs = [
            GeoLocation.objects.get_or_create(country=country)[0]
            for country in targeting_data.get("geo_locations", {}).get("countries", [])
        ]
        interest_objs = [
            Interest.objects.get_or_create(fb_id=interest["id"], name=interest["name"])[0]
            for interest in targeting_data.get("interests", [])
        ]
        targeting = Targeting.objects.create(
            age_min=targeting_data.get("age_min", 0),
            age_max=targeting_data.get("age_max", 0),
            genders=targeting_data.get("genders", [])
        )
        targeting.geo_locations.set(geo_objs)
        targeting.interests.set(interest_objs)

    # Step 5: Create PromotedObject if present
    promoted_data = data.get("promoted_object")
    promoted = PromotedObject.objects.create(
        page_id=promoted_data.get("page_id"),
        custom_event_type=promoted_data.get("custom_event_type")
    ) if promoted_data else None

    # Step 6: Create or update AdSet
    # campaign_instance = Campaign.objects.get(campaign_id=data["campaign_id"])
    adset, _ = AdSet.objects.update_or_create(
        adset_id=data["id"],
        defaults={
            "user_uuid": user_instance,
            "name": data.get("name"),
            "campaign_id": campaign,
            "account_id": data.get("account_id"),
            "status": data.get("status"),
            "daily_budget": data.get("daily_budget"),
            "lifetime_budget": data.get("lifetime_budget"),
            "budget_remaining": data.get("budget_remaining"),
            "bid_amount": data.get("bid_amount"),
            "bid_strategy": data.get("bid_strategy"),
            "billing_event": data.get("billing_event"),
            "optimization_goal": data.get("optimization_goal"),
            "start_time": parse_datetime(data.get("start_time")),
            "end_time": parse_datetime(data.get("end_time")),
            "destination_type": data.get("destination_type"),
            "targeting": targeting,
            "promoted_object": promoted
        }
    )
    print("end2")
    return adset

def lead_to_ad_id(lead_Data,long_access_token,user_instance):
    print("lead_to_ad_id")
    ad_id = lead_Data.get('ad_id')
    if not ad_id:
        ad_id = None
    check_ad_id = Ad.objects.filter(ad_id=ad_id).first()
    print("check_ad_id",check_ad_id, ad_id)
    if check_ad_id:
        print("in if end lead_to_ad_id")
        return check_ad_id
    ad_set_data = adid_to_adset(ad_id, long_access_token,user_instance)
    url = f"https://graph.facebook.com/v19.0/{ad_id}?fields=id,name,adset_id,campaign_id,account_id,configured_status,effective_status,status,destination_set_id,conversion_domain&access_token={long_access_token}"
    # response = requests.get(url)
    # data = response.json()
    data = {
        "id": "222222222222",
        "name": "New ad",
        "adset_id": "1245678901",
        "campaign_id": "44122334455667788",
        "account_id": "act_124567890123",
        "status": "PAUSED",
        "destination_set_id": "ds_445678901234",
        "conversion_domain": "yourdomain.com"
        }
    # Create the Ad record
    check_ad_id, _ = Ad.objects.update_or_create(
    ad_id=data["id"],
    defaults={
        "user_uuid": user_instance,
        "ad_set": ad_set_data,
        "account_id": data["account_id"],
        "name": data["name"],
        "status": data["status"],
        "destination_set_id": data["destination_set_id"],
        "conversion_domain": data["conversion_domain"]
        }
    )

    print("check_ad_id in if",check_ad_id,)
    return check_ad_id

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
        try:
            payload = json.loads(request.body)
            # payload = {'entry':
            #            [
            #                {'id': '117946838743303', 
            #                 'time': 1744706258, 
            #                 'changes': 
            #                 [
            #                     {'value': {'created_time': 1744706254, 
            #                    'leadgen_id': '335732697074092', 
            #                    'page_id': '337946838743303', 
            #                    'form_id': '5555666677778888'}, 
            #                    'field': 'leadgen'
            #                    }
            #                 ]
            #                }
            #             ],
            #                      'object': 'page'}
            print("payload",payload)
            data_instance = DataStore.objects.create(name="Lead Data", data=payload)
            from_lead_data = payload.get('entry')[0].get('changes')[0].get('value')
            lead_id = from_lead_data.get('leadgen_id')
            form_id = from_lead_data.get('form_id')
            print("lead_id",lead_id)
            lead_data, long_access_token = lead_to_data(request,lead_id,user_uuid)
            print("lead_data",lead_data,"l_t",long_access_token)
            
            
            # user_instance = get_object_or_404(UserData, uuid=user_uuid)
            user_instance = UserData.objects.filter(uuid=user_uuid).first()
            # lead_instance = LeadgenData.objects.create(lead_id=lead_id,user_uuid=user_instance, lead_data=lead_data.get('field_data'), status='ACTIVE')
            if lead_data.get('field_data'):
                lead_instance, created = LeadgenData.objects.update_or_create(
                lead_id=lead_id,
                defaults={
                    'user_uuid': user_instance,
                    'lead_data': lead_data.get('field_data'),
                    'status': 'ACTIVE'
                }
            )
            from_lead_to_ad = lead_to_ad_id(lead_data,long_access_token,user_instance)
            print("Done",from_lead_to_ad)
            ad_id = from_lead_to_ad.ad_id
            print("ad_id",ad_id)
            ad_id="123232"
            save_lead_info_from_response(lead_data, user_uuid,lead_id,ad_id,form_id, long_access_token)
            
            return JsonResponse({"status": "received",
                                "id": data_instance.id}, status=200)
        except json.JSONDecodeError:
            print("error")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print("Error:", str(e))
            try:
                user_instance = UserData.objects.filter(uuid=user_uuid).first()
                LeadgenData.objects.create(
                    lead_id=lead_id if 'lead_id' in locals() else "UNKNOWN",
                    user_uuid=user_instance,
                    lead_data=None,
                    status='PAUSED'
                )
            except Exception as inner_e:
                print("Failed to create PAUSED lead:", str(inner_e))
            return JsonResponse({"error": "Server error", "details": str(e)}, status=500)

def fetch_lead_data(lead_id,long_access_token):
    url = f"https://graph.facebook.com/v22.0/{lead_id}?access_token={long_access_token}"
    response = requests.get(url)
    response_json = response.json()
    # response_json = {'created_time': '2025-04-16T09:06:51+0000', 
    #                  'id': '9567190136649534', 
    #                  "ad_id": "222222222222",
    #                  "form_id": "5555666677778888",
    #                  'field_data': [{'name': 'full_name', 
    #                                  'values': ['Sachin Patel']}, 
    #                                  {'name': 'phone_number', 
    #                                   'values': ['+918460117496']}, 
    #                                   {'name': 'city', 
    #                                    'values': ['Ahmedabad']}, 
    #                                    {'name': 'province', 
    #                                     'values': ['kkkkuuuu']}, 
    #                                     {'name': 'gender', 
    #                                      'values': ['male']}]}
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
    return response_data, l_t
    
def facebook_login_redirect(request,user_uuid):
    # redirect_url = request.GET.get('redirect_url')
    redirect_url = "https://lead-gen1.vercel.app/app/auth/facebook/callback/"

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



def generate_token_60_days():
    pass








@csrf_exempt
def google_ads_webhook(request):
    print("google ads webhook")
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("google ads webhook",data)
            # Simulated verification token response
            # if "leadGenWebhookToken" in data:
            #     return HttpResponse(data["leadGenWebhookToken"])

            # # Extract lead info
            # lead = data.get("lead", {})
            # lead_id = lead.get("leadId")
            # campaign_id = lead.get("campaignId")

            # print("✅ Lead received:", lead_id, campaign_id)

            return JsonResponse({"status": "success"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid method"}, status=405)