from django.urls import path
from . import views
from django.http import HttpResponse


urlpatterns = [
 #   path('view/', views.view_licenses, name='view_licenses'),
    path("api/verify-license/", views.verify_license, name="verify_license"),
      path('api/bind-hwid/', views.bind_hwid, name='bind_hwid'),  # A URL for the 'view_licenses' view
]
