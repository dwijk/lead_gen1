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
    # Add required foreign key
    cleaned_data["user_uuid"] = user_uuid
    user_instance = UserData.objects.get(uuid=user_uuid)
    lead_data = LeadgenData.objects.filter(lead_id=lead_id).first()
    # Update cleaned_data to contain the instance instead of UUID
    cleaned_data["user_uuid"] = user_instance
    cleaned_data["lead_id"] = lead_data.get('lead_id')
    cleaned_data["ad_id"] = ad_id
    form_name = formid_to_name(form_id,long_access_token)
    cleaned_data["form_name"] = form_name
    print("cleaned_data",cleaned_data)
    # Save the object
    lead = UserLeadInfo.objects.create(**cleaned_data)
    return True

def adset_to_campaign(adset_id, long_access_token):
    url = f"https://graph.facebook.com/v22.0/{adset_id}?fields=campaign_id&access_token={long_access_token}"
    response = requests.get(url)
    response_json = response.json()
#     response_json = {
#   "campaign_id": "44122334455667788",
#   "id": "441234567890123456"
# }

    campaign_id = response_json.get('campaign_id')
    print("campaign_id",campaign_id)
    campaign = Campaign.objects.filter(campaign_id=campaign_id).first()
    if not campaign:
        # campaign URL
        print("in if campaign_data")
        campaign_url = f"https://graph.facebook.com/v22.0/{campaign_id}?fields=id,name,status,budget_remaining,objective,start_time,stop_time,daily_budget,lifetime_budget&access_token={long_access_token}"
        campaign_response = requests.get(campaign_url)
        campaign_data = campaign_response.json()
        # campaign_data = {
        #     "id": "44122334455667788",
        #     "name": "My Campaign",
        #     "status": "ACTIVE",
        #     "budget_remaining": "1000000",
        #     "objective": "LEAD_GENERATION",
        #     "start_time": "2025-04-01T00:00:00+0000",
        #     "stop_time": "2025-04-30T23:59:59+0000",
        #     "daily_budget": "50000",
        #     "lifetime_budget": "1500000"
        #     }

        # Extract data with safe defaults
        name = campaign_data.get('name')
        status = campaign_data.get('status')
        budget_remaining = campaign_data.get('budget_remaining') or 0
        objective = campaign_data.get('objective')
        start_time = campaign_data.get('start_time')
        stop_time = campaign_data.get('stop_time')
        daily_budget = campaign_data.get('daily_budget') or 0
        lifetime_budget = campaign_data.get('lifetime_budget') or 0

        # Step 4: Create and save campaign
        campaign = Campaign.objects.create(
            campaign_id=campaign_id,
            name=name,
            effective_status=status,
            budget_remaining=budget_remaining,
            objective=objective,
            start_time=start_time,
            end_time=stop_time,
            daily_budget=daily_budget,
            lifetime_budget=lifetime_budget
        )
        print("campaign",campaign)
    return campaign
    
def adid_to_adset(ad_id, long_access_token):
    print("ad_id",ad_id, "long_access_token",long_access_token)
    url = f"https://graph.facebook.com/v22.0/{ad_id}?fields=adset_id&access_token={long_access_token}"
    response = requests.get(url)
    response_json = response.json()
    # response_json = {
    #     "adset_id": "442345678901",
    #     "id": "44987654321098765"
    #     }       
    adset_id = response_json.get('adset_id')
    print("adset_id",adset_id)
    # check_adset_id = AdSet.objects.filter(ad_set_id=adset_id).first()
    check_adset_id = AdSet.objects.select_related(
        'targeting', 'promoted_object', 'campaign_id'
    ).prefetch_related(
        Prefetch('targeting__geo_locations'),
        Prefetch('targeting__interests')
    ).filter(adset_id=adset_id).first()
    print("check_adset",check_adset_id)
    if not check_adset_id:
        print("check_adset_id not found")
        # campaign_data = adset_to_campaign(adset_id, long_access_token)
        # print("campaign",campaign_data)
        # ADSET URL
        url = f"https://graph.facebook.com/v19.0/{adset_id}?fields=id,name,campaign_id,account_id,status,daily_budget,lifetime_budget,budget_remaining,bid_amount,bid_strategy,billing_event,optimization_goal,start_time,end_time,destination_type,targeting{{age_min,age_max,genders,geo_locations{{countries}},interests{{id,name}}}},promoted_object{{page_id,custom_event_type}}&access_token={long_access_token}"
        response = requests.get(url)
        data = response.json()
        # data = {
        #     "id": "442345678901",
        #     "name": "Ad Set 1",
        #     "campaign_id": "44122334455667788",
        #     "account_id": "act_441234567890",
        #     "status": "ACTIVE",
        #     "daily_budget": "10000",
        #     "lifetime_budget": "500000",
        #     "budget_remaining": "450000",
        #     "bid_amount": 200,
        #     "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
        #     "billing_event": "IMPRESSIONS",
        #     "optimization_goal": "LEAD_GENERATION",
        #     "start_time": "2025-04-10T00:00:00+0000",
        #     "end_time": "2025-04-30T23:59:00+0000",
        #     "destination_type": "WEBSITE",
        #     "targeting": {
        #         "age_min": 25,
        #         "age_max": 45,
        #         "genders": [1],
        #         "geo_locations": {
        #         "countries": ["US"]
        #         },
        #         "interests": [
        #         {
        #             "id": "4416003139266461",
        #             "name": "Technology"
        #         },
        #         {
        #             "id": "446003337891234",
        #             "name": "Startups"
        #         }
        #         ]
        #     },
        #     "promoted_object": {
        #         "page_id": "44123456789012345",
        #         "custom_event_type": "LEAD"
        #     }
        #     }

        geo_objs = []
        interest_objs = []

        if 'targeting' in data:
            targeting_data = data['targeting']

            # Save countries
            for country in targeting_data.get("geo_locations", {}).get("countries", []):
                geo, _ = GeoLocation.objects.get_or_create(country=country)
                geo_objs.append(geo)
            print("geo_objs",geo_objs)
            # Save interests
            for interest in targeting_data.get("interests", []):
                i, _ = Interest.objects.get_or_create(fb_id=interest["id"], name=interest["name"])
                interest_objs.append(i)
            print("interest_objs",interest_objs)
            targeting = Targeting.objects.create(
                age_min=targeting_data.get("age_min", 0),
                age_max=targeting_data.get("age_max", 0),
                genders=targeting_data.get("genders", [])
            )
            targeting.geo_locations.set(geo_objs)
            targeting.interests.set(interest_objs)
            print("targeting",targeting)
        else:
            targeting = None

        # Promoted Object
        if "promoted_object" in data:
            promoted = PromotedObject.objects.create(
                page_id=data["promoted_object"].get("page_id"),
                custom_event_type=data["promoted_object"].get("custom_event_type")
            )
            print("promoted",promoted)
        else:
            promoted = None
            print("promoted",promoted)
        # Create AdSet
        print("campaign_data",data["campaign_id"])
        campaign_instance = Campaign.objects.get(campaign_id=data["campaign_id"])
        print("campaign_instance",campaign_instance)
        check_adset_id, created = AdSet.objects.update_or_create(
            adset_id=data.get("id"),
            defaults={
                "adset_id":data.get("id"),
                "name": data.get("name"),
                "campaign_id": campaign_instance,
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
        print("adset",check_adset_id)
    return check_adset_id

def lead_to_ad_id(lead_Data,long_access_token):
    print("lead_Data",lead_Data)
    ad_id = lead_Data.get('ad_id')
    print("ad_id",ad_id)
    check_ad_id = Ad.objects.filter(ad_id=ad_id).first()
    print("check_ad_id",check_ad_id)
    if not check_ad_id:
        print("check_ad_id not found", ad_id, long_access_token)
        ad_set_data = adid_to_adset(ad_id, long_access_token)
        print("ad_set_data2",ad_set_data, "type",type(ad_set_data))
        url = f"https://graph.facebook.com/v19.0/{ad_id}?fields=id,name,adset_id,campaign_id,account_id,configured_status,effective_status,status,destination_set_id,conversion_domain&access_token={long_access_token}"
        response = requests.get(url)
        data = response.json()
        # data = {
        #     "id": "222222222222",
        #     "name": "New ad",
        #     "adset_id": "1245678901",
        #     "campaign_id": "44122334455667788",
        #     "account_id": "act_124567890123",
        #     "status": "PAUSED",
        #     "destination_set_id": "ds_445678901234",
        #     "conversion_domain": "yourdomain.com"
        #     }
        # Create the Ad record
        check_ad_id = Ad.objects.create(
            ad_set=ad_set_data,
            ad_id=data.get("id"),
            account_id=data.get("account_id"),
            name=data.get("name"),
            status=data.get("status"),
            destination_set_id=data.get("destination_set_id"),
            conversion_domain=data.get("conversion_domain")
        )

        print("check_ad_id in if",check_ad_id)
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
        print("post")
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
            #                    'form_id': '3314913513600972'}, 
            #                    'field': 'leadgen'
            #                    }
            #                 ]
            #                }
            #             ],
            #                      'object': 'page'}
            print("payload",payload)
            data_instance = DataStore.objects.create(name="Lead Data", data=payload)
            lead_id = payload.get('entry')[0].get('changes')[0].get('value').get('leadgen_id')
            form_id = payload.get('entry')[0].get('changes')[0].get('value').get('form_id')
            print("lead_id",lead_id)
            lead_data, long_access_token = lead_to_data(request,lead_id,user_uuid)
            print("lead_data",lead_data)
            print("l_t",long_access_token)
            ad_id="123232"
            save_lead_info_from_response(lead_data, user_uuid,lead_id,ad_id,form_id, long_access_token)
            from_lead_to_ad = lead_to_ad_id(lead_data,long_access_token)
            print("Done",from_lead_to_ad)
            ad_id = from_lead_to_ad.ad_id
            
            print("save_lead_info_from_response",save_lead_info_from_response)
            user_instance = get_object_or_404(UserData, uuid=user_uuid)
            user_instance = UserData.objects.filter(uuid=user_uuid).first()
            print("user_instance",user_instance)
            lead_instance = LeadgenData.objects.create(lead_id=lead_id,user_uuid=user_instance, lead_data=lead_data.get('field_data'))
            print("lead_instance",lead_instance)

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