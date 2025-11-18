from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from user.decorators import group_required, role_required

from .serializers import UserSerializer
from .serializers import GroupSerializer


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

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_roles(request):
    roles = Group.objects.all()
    serializer = GroupSerializer(roles, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above (Lead, Phone Analyst, Manager)
def edit_user_roles(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    new_role_names = request.data.get('roles', [])
    if not isinstance(new_role_names, list):
        return Response({'detail': 'Roles must be a list of role names.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Clear existing groups and add new ones
    user.groups.clear()
    for role_name in new_role_names:
        try:
            group = Group.objects.get(name=role_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            return Response({'detail': f'Role "{role_name}" not found.'}, status=status.HTTP_400_BAD_REQUEST)
            
    serializer = UserSerializer(user)
    return Response(serializer.data)

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
        
        # Assign 'Tech' role by default
        try:
            tech_group = Group.objects.get(name='Tech')
            user.groups.add(tech_group)
        except Group.DoesNotExist:
            print("'Tech' group does not exist. Please ensure migrations have been run.")

        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({f"passed for {request.user.email}"})
