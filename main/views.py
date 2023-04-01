from accounts.models import ActivityLog
from .serializers import EventPreferenceSerializer, LovedOneProfileSerializer, SubscribeSerializer, SubscriptionSerializer
from .models import EventPreference, LovedOneProfile, Subscription, get_current_subscription, SMSResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes, action
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView, RetrieveAPIView
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from accounts.helpers.vonage_api import sms
from accounts.helpers.gpt import get_ai_response
import json
from django.http import HttpResponse

class ProfileView(ListCreateAPIView):
    queryset = LovedOneProfile.objects.filter(is_deleted=False)
    serializer_class = LovedOneProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
         
        if request.user.role == "user":
            queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    @swagger_auto_schema(method="post", request_body= LovedOneProfileSerializer())
    @action(methods=["post"], detail=True)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            ActivityLog.objects.create(
                user=instance.user,
                action = f"Created a new profile for a loved one"
                )
            return Response({"message":"success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class ProfileDetailView(RetrieveUpdateDestroyAPIView):
    queryset = LovedOneProfile.objects.filter(is_deleted=False)
    serializer_class = LovedOneProfileSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"
    
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
    @swagger_auto_schema(method="put", request_body= LovedOneProfileSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        
        return self.update(request, *args, **kwargs)

    
    @swagger_auto_schema(method="put", request_body= LovedOneProfileSerializer())
    @action(methods=["put"], detail=True)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        
        return self.partial_update(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        
        return self.destroy(request, *args, **kwargs)
    
    
    
    
    

class EventPreferenceView(CreateAPIView):
    queryset = EventPreference.objects.filter(is_deleted=False)
    serializer_class = EventPreferenceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    
    
    @swagger_auto_schema(method="post", request_body= EventPreferenceSerializer())
    @action(methods=["post"], detail=True)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            ActivityLog.objects.create(
                user=instance.user,
                action = f"Created a event preference for a loved one"
                )
            return Response({"message":"success"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


class EventPreferenceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = EventPreference.objects.filter(is_deleted=False)
    serializer_class = EventPreferenceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    
    @swagger_auto_schema(method="put", request_body= LovedOneProfileSerializer())
    @action(methods=["put"], detail=True)
    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        
        return self.update(request, *args, **kwargs)

    
    @swagger_auto_schema(method="put", request_body= LovedOneProfileSerializer())
    @action(methods=["put"], detail=True)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        
        return self.partial_update(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user != instance.user:
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        
        return self.destroy(request, *args, **kwargs)
    
    
class SubscriptionListView(ListAPIView):
    
    queryset = Subscription.objects.filter(is_deleted=False)
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
         
        if request.user.role == "user":
            queryset = queryset.filter(user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    
    

class SubscriptionDetailView(RetrieveAPIView):
    queryset = Subscription.objects.filter(is_deleted=False)
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    lookup_field = "id"
    
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        if request.user.role=="user" and request.user != instance.user:
            
            raise PermissionDenied(detail={"message":"you do not have permission to perform this action"})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    

@swagger_auto_schema(method="post", request_body= SubscribeSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def subscribe(request):
    
    "make a new subscription for logged in user"
    
    end_date = {
        "annual" : timezone.now() + relativedelta(years=1),
        "monthly" : timezone.now() + relativedelta(months=1)
    }
    
    if request.method == "POST":
        
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        
        current_sub = get_current_subscription(user=user)
        
        if current_sub is None or current_sub.has_expired:
            Subscription.objects.create(**serializer.validated_data, 
                                        user=user,
                                        start_date=timezone.now(),
                                        end_date = end_date.get(serializer.validated_data.get("subscription_type"))
                                        )
            return Response({"message":"subscription successful"}, status=status.HTTP_201_CREATED)
        
        return Response({"message":"cannot create subscription because a subscription is already in use"}, status=status.HTTP_400_BAD_REQUEST)
    
    

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def check_subscription(request):
    
    """Verify if the user has an existing subscription"""
    
    
    user = request.user
        
        
    current_sub = get_current_subscription(user=user)
    
    if current_sub is None or current_sub.has_expired:
        return Response({"message":"no subscription in use"}, status=status.HTTP_402_PAYMENT_REQUIRED)
    
    
    
    return Response({"message":f"subscription is currently active."}, status=status.HTTP_200_OK)






@api_view("POST")
def receive_sms(request):
   
    if request.method == 'POST':
        data = request.POST

        # Remove the array from each value
        clean_data = {k: v[0] for k, v in data.items()}
        
        print(clean_data)

        ai_prompt = clean_data.get("text")
        
        print(ai_prompt)
        
        message = get_ai_response(ai_prompt)
        
        text = message.get("choices")[0].get("text")
        
        print(text)

        res = sms.send_message(
                    {
                        "from": "Doting App",
                        "to": clean_data.get("msisdn"),
                        "text": text,
                    }
                )
        
        print(res)
        
        SMSResponse.objects.create(
            text_json = json.dumps(clean_data),
            ai_response = message,
        )

    return HttpResponse(status=204)
    