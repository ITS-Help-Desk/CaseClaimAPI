from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from user.decorators import group_required, role_required, get_user_highest_role_level, ROLE_HIERARCHY

from django.contrib.auth.models import User
from django.db.models import Q

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
        {
            'Endpoint': '/create-ping/',
            'method': 'POST',
            'body': {
                'casenum': 'case number',
                'tech_id': 'user id of the tech to ping',
                'severity': 'pingedlow | pingedmed | pingedhigh',
                'comment': 'description of the issue'
            },
            'description': 'Creates a manual ping without going through the review workflow (Lead only).'
        },
    ]
    return Response(routes)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_pings_for_user(request, pk):
    user =  User.objects.get(pk=pk)

    # Check if user has Lead or above permission (hierarchical)
    user_level = get_user_highest_role_level(request.user)
    lead_level = ROLE_HIERARCHY.get('Lead', 0)
    is_lead_or_above = user_level >= lead_level
    
    if not is_lead_or_above and request.user != user:
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
@role_required('Lead')  # Lead and above (hierarchical)
def list_reviewed_claims(request):
    claims = ReviewedClaim.objects.all()
    serializer = ReviewedClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Tech')  # Tech and above (hierarchical)
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
        claim.acknowledge_comment = request.data.get('acknowledge_comment', '')
        claim.save()
        
        serializer = ReviewedClaimSerializer(claim)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except ReviewedClaim.DoesNotExist:
        return Response({'error': 'Ping not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above (hierarchical)
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


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above (hierarchical)
def create_manual_ping(request):
    """
    Creates a manual ping without going through the normal review workflow.
    
    This allows leads to ping a tech about a case directly, useful for:
    - Cases from external sources
    - Follow-up issues discovered later
    - Quality coaching outside the normal review process
    
    Required fields:
        - casenum: The case number
        - tech_id: User ID of the tech to ping
        - severity: 'pingedlow', 'pingedmed', or 'pingedhigh'
        - comment: Description of the issue
    """
    from django.utils import timezone
    
    # Validate required fields
    required_fields = ['casenum', 'tech_id', 'severity', 'comment']
    missing_fields = [f for f in required_fields if f not in request.data]
    
    if missing_fields:
        return Response(
            {'error': f'Missing required fields: {", ".join(missing_fields)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    casenum = request.data.get('casenum')
    tech_id = request.data.get('tech_id')
    severity = request.data.get('severity')
    comment = request.data.get('comment')
    
    # Validate severity
    valid_severities = ['pingedlow', 'pingedmed', 'pingedhigh']
    if severity not in valid_severities:
        return Response(
            {'error': f'Invalid severity. Must be one of: {", ".join(valid_severities)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate tech exists
    try:
        tech = User.objects.get(pk=tech_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Tech user not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create the ping (as a ReviewedClaim)
    now = timezone.now()
    
    ping = ReviewedClaim.objects.create(
        casenum=casenum,
        tech_id=tech,
        lead_id=request.user,  # The lead creating the ping
        claim_time=now,  # For manual pings, we use current time
        complete_time=now,
        status=severity,
        comment=comment
    )
    
    serializer = ReviewedClaimSerializer(ping)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
