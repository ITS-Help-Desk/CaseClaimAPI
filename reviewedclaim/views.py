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
        {
            'Endpoint': '/acknowledge/<int:pk>/',
            'method': 'POST',
            'body': {'acknowledge_comment': ''},
            'description': 'Acknowledges a pinged claim (Tech only - own pings).'
        },
        {
            'Endpoint': '/resolve/<int:pk>/',
            'method': 'POST',
            'body': None,
            'description': 'Marks an acknowledged ping as resolved (Lead only).'
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
        status__in=['resolved', 'pingedlow', 'pingedmed', 'pingedhigh', 'acknowledged']
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

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@group_required('Tech')
def acknowledge_ping(request, pk):
    """
    Allows a Tech to acknowledge a ping (only their own pings).
    Changes status from pingedlow/pingedmed/pingedhigh to 'acknowledged'.
    """
    try:
        claim = ReviewedClaim.objects.get(pk=pk)
        
        # Verify this is a ping status
        if claim.status not in ['pingedlow', 'pingedmed', 'pingedhigh']:
            return Response(
                {'error': 'This claim is not in a pinged state.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the user is the tech who owns this case
        if claim.tech_id != request.user:
            return Response(
                {'error': 'You can only acknowledge your own pings.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the claim
        claim.status = 'acknowledged'
        claim.acknowledged_by = request.user
        claim.acknowledge_time = timezone.now()
        claim.acknowledge_comment = request.data.get('acknowledge_comment', '')
        claim.save()
        
        serializer = ReviewedClaimSerializer(claim)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ReviewedClaim.DoesNotExist:
        return Response({'error': 'Ping not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@group_required('Lead')
def resolve_ping(request, pk):
    """
    Allows a Lead to mark an acknowledged ping as resolved.
    Changes status from 'acknowledged' to 'resolved'.
    """
    try:
        claim = ReviewedClaim.objects.get(pk=pk)
        
        # Verify this is in acknowledged state
        if claim.status != 'acknowledged':
            return Response(
                {'error': 'This claim must be acknowledged before it can be resolved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the status to resolved
        claim.status = 'resolved'
        claim.save()
        
        serializer = ReviewedClaimSerializer(claim)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ReviewedClaim.DoesNotExist:
        return Response({'error': 'Ping not found'}, status=status.HTTP_404_NOT_FOUND)
