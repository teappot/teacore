from django.http import HttpRequest

#from ecommerce.models import Order, OrderItem
from teacore.track.MetaAPI import MetaAPI
from teacore.track.TrackEvents import TrackEvents
from facebook_business.adobjects.serverside.user_data import UserData
from facebook_business.adobjects.serverside.custom_data import CustomData
from facebook_business.adobjects.serverside.content import Content
from django.contrib.auth.models import User

class TrackAPI:

    """
    Clase para manejar el tracking de eventos con Meta (Facebook)
    Funciona como interfaz para MetaAPI y GTAG (en el futuro)
    """

    def __init__(self):
        self.meta = MetaAPI()


    def __remote_ip(self, request: HttpRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]  # Take the first IP if multiple are present
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def add(self, events:list, request: HttpRequest, **kwargs):
        
        for event in events:
            match event:
                case TrackEvents.ADD_TO_CART: self.add_to_cart(request, **kwargs)
                case TrackEvents.INITIATE_CHECKOUT: self.initiate_checkout(request, **kwargs)
                case TrackEvents.LEAD: self.lead(request, **kwargs)
                case TrackEvents.PURCHASE: self.purchase(request, **kwargs)
                case TrackEvents.VIEW_CONTENT: self.view_content(request, **kwargs)


    """
    # Mover a ecommerce
    def add_to_cart(self, request: HttpRequest, user:User, order_item:OrderItem, phone:str="",):
        if not self.meta.init: return
        
        user_data = UserData(
            emails=[user.email],
            phones=[phone],
            first_name=user.first_name,
            last_name=user.last_name,
            client_ip_address=self.__remote_ip(request) if request else "",
            client_user_agent=request.headers['User-Agent'] if request else "",
            fbc=request.COOKIES.get('_fbc') if request else "",
            fbp=request.COOKIES.get('_fbp') if request else "",
        )
        
        content = Content(
            product_id=order_item.variant.sku if order_item.variant.sku else order_item.variant.id,
            quantity=float(order_item.quantity),
            item_price=float(order_item.price),
            title=order_item.variant.product.name,
            description=order_item.variant.description,
            category=order_item.variant.product.type.name if order_item.variant.product.type else "",
        )

        custom_data = CustomData(
            order_id=str(order_item.order.uuid),
            contents=[content],
            currency=order_item.order.currency.code,
            value=float(order_item.order.total),
        )
        
        self.meta.add_to_cart(
            request=request,
            user_data=user_data,
            custom_data=custom_data,
        )

    def initiate_checkout(self, request: HttpRequest, order:Order):
        if not self.meta.init: return
        
        user_data = UserData(
            emails=[order.customer.user.email],
            first_name=order.customer.user.first_name,
            last_name=order.customer.user.last_name,
            client_ip_address=self.__remote_ip(request) if request else "",
            client_user_agent=request.headers['User-Agent'] if request else "",
            fbc=request.COOKIES.get('_fbc') if request else "",
            fbp=request.COOKIES.get('_fbp') if request else "",
        )

        contents = []
        for order_item in order.items():
            contents.append(Content(
                product_id=order_item.variant.sku if order_item.variant.sku else order_item.variant.id,
                quantity=float(order_item.quantity),
                item_price=float(order_item.price),
                title=order_item.variant.product.name,
                description=order_item.variant.description,
                category=order_item.variant.product.type.name if order_item.variant.product.type else "",
            ))

        custom_data = CustomData(
            order_id=str(order.uuid),
            contents=contents,
            currency=order.currency.code,
            value=float(order.total),
        )

        self.meta.initiate_checkout(
            request=request,
            user_data=user_data,
            custom_data=custom_data,
        )

    def purchase(self, request: HttpRequest, order:Order):
        if not self.meta.init: return
        
        user_data = UserData(
            emails=[order.customer.user.email],
            first_name=order.customer.user.first_name,
            last_name=order.customer.user.last_name,
            client_ip_address=self.__remote_ip(request) if request else "",
            client_user_agent=request.headers['User-Agent'] if request else "",
            fbc=request.COOKIES.get('_fbc') if request else "",
            fbp=request.COOKIES.get('_fbp') if request else "",
        )

        contents = []
        for order_item in order.items():
            contents.append(Content(
                product_id=order_item.variant.sku if order_item.variant.sku else order_item.variant.id,
                quantity=float(order_item.quantity),
                item_price=float(order_item.price),
                title=order_item.variant.product.name,
                description=order_item.variant.description,
                category=order_item.variant.product.type.name if order_item.variant.product.type else "",
            ))

        custom_data = CustomData(
            order_id=str(order.uuid),
            contents=contents,
            currency=order.currency.code,
            value=float(order.total),
        )

        self.meta.purchase(
            request=request,
            user_data=user_data,
            custom_data=custom_data,
        )
    """

    def lead(self, request: HttpRequest, user:User, phone:str):
        if not self.meta.init: return
        
        user_data = UserData(
            emails=[user.email],
            phones=[phone],
            first_name=user.first_name,
            last_name=user.last_name,
            client_ip_address=self.__remote_ip(request) if request else "",
            client_user_agent=request.headers['User-Agent'] if request else "",
            fbc=request.COOKIES.get('_fbc') if request else "",
            fbp=request.COOKIES.get('_fbp') if request else "",
        )

        self.meta.lead(
            request=request,
            user_data=user_data,
        )


    def view_content(self, request: HttpRequest, user:User=None):
        if not self.meta.init: return
        if not user: 
            user = request.user if request.user.is_authenticated else None

        user_data = UserData(
            emails=[user.email] if user else [],
            first_name=user.first_name if user else "",
            last_name=user.last_name if user else "",
            client_ip_address=self.__remote_ip(request) if request else "",
            client_user_agent=request.headers['User-Agent'] if request else "",
            fbc=request.COOKIES.get('_fbc') if request else "",
            fbp=request.COOKIES.get('_fbp') if request else "",
        )

        self.meta.view_content(
            request=request,
            user_data=user_data,
        )