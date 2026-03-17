from django.urls import path

from . import views

app_name = "teacore"
urlpatterns = [
    
    path("template/<str:template>/", views.template, name="template"),
    path("widget/<str:slug>/", views.widget, name="widget"),
    
    # Admin custom actions URLs
    path("admin/<str:app_label>/<str:model_name>/<int:id>/<str:method_name>/", views.admin, name="admin"),

]