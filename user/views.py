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
from .models import UserProfile


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/login/',
            'method': 'POST',
            'body': {'username': '', 'password': ''},
            'description': 'Returns an authorization token and user information. If must_reset_password is true, user must call /reset-password/ before accessing other endpoints.'
        },
        {
            'Endpoint': '/signup/',
            'method': 'POST',
            'body': {'username': '', 'password': '', 'email': '', 'first_name': '', 'last_name': '', 'discord_id': '(optional)'},
            'description': 'Creates a new user and returns an authorization token and user information'
        },
        {
            'Endpoint': '/reset-password/',
            'method': 'POST',
            'body': {'new_password': ''},
            'description': 'Resets the password for users who must_reset_password is true (migrated users)'
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
    
    # Check if user needs to reset password
    must_reset = False
    if hasattr(user, 'profile') and user.profile.must_reset_password:
        must_reset = True
    
    return Response({
        "token": token.key, 
        "user": serializer.data,
        "must_reset_password": must_reset
    })

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        
        # Ensure profile exists (serializer should create it, but just in case)
        if not hasattr(user, 'profile'):
            discord_id = request.data.get('discord_id')
            UserProfile.objects.create(user=user, discord_id=discord_id)
        
        # New users start with NO roles - roles must be assigned by Lead/Manager
        # No automatic role assignment

        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def reset_password(request):
    """
    Allows a user to reset their password. 
    Required for migrated users who have must_reset_password=True.
    """
    new_password = request.data.get('new_password')
    
    if not new_password:
        return Response(
            {"detail": "new_password is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 6:
        return Response(
            {"detail": "Password must be at least 6 characters."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = request.user
    user.set_password(new_password)
    user.save()
    
    # Clear the must_reset_password flag
    if hasattr(user, 'profile'):
        user.profile.must_reset_password = False
        user.profile.save()
    
    # Generate new token (old one invalidated by password change)
    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)
    
    return Response({
        "detail": "Password reset successfully.",
        "token": token.key
    })

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({f"passed for {request.user.email}"})
