from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from user.decorators import group_required, role_required

from completeclaim.models import CompleteClaim
from completeclaim.serializers import CompleteClaimSerializer
from reviewedclaim.models import ReviewedClaim
from reviewedclaim.serializers import ReviewedClaimSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/review/<int:pk>/',
            'method': 'POST',
            'body': {'status': '', 'comment': ''},
            'description': 'Reviews a completed claim by creating a reviewed claim. Supports all statuses: checked, done, pingedlow, pingedmed, pingedhigh, acknowledged, resolved, kudos.'
        },
        {
            'Endpoint': '/begin-review/<int:pk>/',
            'method': 'POST',
            'body': None,
            'description': 'Begins a review of a claim (prevents other leads from reviewing).'
        },
        {
            'Endpoint': '/list/',
            'method': 'GET',
            'body': None,
            'description': 'Lists all complete claims.'
        },
    ]
    return Response(routes)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above (hierarchical)
def begin_review(request, pk):
    try:
        claim = CompleteClaim.objects.get(pk=pk)
        claim.lead_id = request.user
        claim.save()

        serializer = CompleteClaimSerializer(claim)

        # Notify WebSocket
        async_to_sync(get_channel_layer().group_send)(
            "caseflow",
            {
                "type": "completeclaim",
                "event": "begin-review",
                "casenum": claim.casenum,
                "user": claim.lead_id.username
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except CompleteClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above (hierarchical)
def review_complete_claim(request, pk):
    try:
        claim = CompleteClaim.objects.get(pk=pk)
        tech = claim.user_id
        lead = request.user
        status_value = request.data.get('status')
        comment = request.data.get('comment', '')

        if not tech or not lead or not status_value:
            return Response({'error': 'Status are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        new_claim = ReviewedClaim.objects.create(
            casenum=claim.casenum,
            tech_id=tech,
            lead_id=lead,
            claim_time=claim.claim_time,
            complete_time=claim.complete_time,
            status=status_value,
            comment=comment
        )

        claim.delete()

        serializer = ReviewedClaimSerializer(new_claim)

        # Notify WebSocket
        async_to_sync(get_channel_layer().group_send)(
            "caseflow",
            {
                "type": "completeclaim",
                "event": "review",
                "casenum": new_claim.casenum,
                "user": new_claim.lead_id.username
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except CompleteClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above (hierarchical)
def list_complete_claims(request):
    claims = CompleteClaim.objects.all()
    serializer = CompleteClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
