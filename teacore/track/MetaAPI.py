import time

from django.http import HttpRequest
from facebook_business.adobjects.serverside.action_source import ActionSource
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.content import Content
from facebook_business.adobjects.serverside.delivery_category import DeliveryCategory
from facebook_business.adobjects.serverside.event import Event
from facebook_business.adobjects.serverside.event_request import EventRequest
from facebook_business.api import FacebookAdsApi

from teacore.track.TrackEvents import TrackEvents
from django.conf import settings

class MetaAPI:

    def __init__(self):
        if not settings.TRACK_TOKENMETA or not settings.TRACK_PIXELMETA:
            self.init = False
            return
        
        FacebookAdsApi.init(access_token=settings.TRACK_TOKENMETA)
        self.token = settings.TRACK_TOKENMETA
        self.pixel = settings.TRACK_PIXELMETA
        self.init = True

    def add_to_cart(self, request: HttpRequest, user_data:UserData, custom_data:CustomData):

        self.send(
            event_name=TrackEvents.ADD_TO_CART, 
            request=request, 
            user_data=user_data, 
            custom_data=custom_data
        )
    
    def initiate_checkout(self, request: HttpRequest, user_data:UserData, custom_data:CustomData):

        self.send(
            event_name=TrackEvents.INITIATE_CHECKOUT, 
            request=request, 
            user_data=user_data, 
            custom_data=custom_data
        )
    
    def purchase(self, request: HttpRequest, user_data:UserData, custom_data:CustomData):

        self.send(
            event_name=TrackEvents.PURCHASE, 
            request=request, 
            user_data=user_data, 
            custom_data=custom_data
        )
    
    def lead(self, request: HttpRequest, user_data:UserData):

        self.send(
            event_name=TrackEvents.LEAD, 
            request=request, 
            user_data=user_data,
        )
    
    def view_content(self, request: HttpRequest, user_data:UserData):

        self.send(
            event_name=TrackEvents.VIEW_CONTENT, 
            request=request, 
            user_data=user_data,
        )
    



    def send(self, event_name:str, request: HttpRequest=None, user_data:UserData = None, custom_data:CustomData = None):
        if not self.init: return
        
        event = Event(
            event_name=event_name,
            event_time=int(time.time()),
            user_data=user_data,
            custom_data=custom_data,
            event_source_url=request.build_absolute_uri() if request else None,
            action_source=ActionSource.WEBSITE,
        )

        events = [event]

        event_request = EventRequest(
            events=events,
            pixel_id=self.pixel,
        )
        
        event_response = event_request.execute()
        print(event_name, event.__dict__, event_response)
        return event_response