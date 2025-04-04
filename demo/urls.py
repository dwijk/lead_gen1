from django.contrib import admin
from django.urls import path, include

from app.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path('app/', include('app.urls')),  # Include the API URLs

]
