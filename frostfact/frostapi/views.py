# views.py
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from base64 import b64decode
from .serializers import *
from django.contrib.auth.models import User

class BaseAuthenticatedView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_credentials(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Basic '):
            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':')
            return username, password
        return None, None

    def authenticate(self, request):
        username, password = self.get_credentials(request)
        if not username or not password:
            raise AuthenticationFailed('Invalid credentials')
        try:
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise AuthenticationFailed('Invalid username/password')
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid username/password')

    def get(self, request, slug=None, *args, **kwargs):
        self.authenticate(request)
        if slug:
            instance = get_object_or_404(self.get_queryset(), slug=slug)
            serializer = self.get_serializer(instance)
        else:
            instances = self.get_queryset()
            serializer = self.get_serializer(instances, many=True)
        return Response(serializer.data)



    def post(self, request, *args, **kwargs):
        self.authenticate(request)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"success": True, "data": serializer.data}, status=201)
        return Response({"success": False, "errors": serializer.errors}, status=400)

class ContactFormApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = ContactFormSubmission.objects.all()
    serializer_class = ContactFormSerializer

class EventApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = EventData.objects.all()
    serializer_class = EventDataSerializer

class ClientApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    ordering_fields = ('start_datetime',)

class PolicyApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = PolicyData.objects.all()
    serializer_class = PolicyDataSerializer

class FaqApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = FAQData.objects.all()
    serializer_class = FaqDataSerializer

class GalleryApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = GalleryData.objects.all()
    serializer_class = GalleryDataSerializer

class TextSliderTopApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = TextSliderTop.objects.filter(active_text=True)
    serializer_class = TextSliderTopSerializer

class TextSliderBottomApiView(BaseAuthenticatedView, generics.ListCreateAPIView):
    queryset = TextSliderBottom.objects.filter(active_text=True)
    serializer_class = TextSliderBottomSerializer
