from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer

@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/login/',
            'method': 'POST',
            'body': {'username': '', 'password': ''},
            'description': 'Returns an authorization token and user information'
        },
        {
            'Endpoint': '/signup/',
            'method': 'POST',
            'body': {'username': '', 'password': '', 'email': '', 'first_name': '', 'last_name': ''},
            'description': 'Creates a new user and returns an authorization token and user information'
        },
        {
            'Endpoint': '/test_token/',
            'method': 'GET',
            'body': None,
            'description': 'Tests if an authorization token is valid (replies with user\'s email)'
        },
    ]
    return Response(routes)

@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({f"passed for {request.user.email}"})
