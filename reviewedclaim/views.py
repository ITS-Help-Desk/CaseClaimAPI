from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from user.decorators import group_required

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from reviewedclaim.models import ReviewedClaim
from reviewedclaim.serializers import ReviewedClaimSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/list/',
            'method': 'GET',
            'body': None,
            'description': 'Lists all reviewed claims.'
        },
        {
            'Endpoint': '/getpings/<int:pk>',
            'method': 'GET',
            'body': None,
            'description': 'Lists all pinged/resolved claims by a given user.'
        },
    ]
    return Response(routes)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_pings_for_user(request, pk):
    user =  User.objects.get(pk=pk)

    is_lead = request.user.groups.filter(name='Lead').exists()
    if not is_lead and request.user != user:
        return Response(
            {"detail": "You do not have permission to view this user's pings."},
            status=status.HTTP_403_FORBIDDEN
        )

    reviewed_claims = ReviewedClaim.objects.filter(
        tech_id=user,
        status__in=['resolved', 'pingedlow', 'pingedmed', 'pingedhigh']
    )

    serializer = ReviewedClaimSerializer(reviewed_claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@group_required('Lead')
def list_reviewed_claims(request):
    claims = ReviewedClaim.objects.all()
    serializer = ReviewedClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
