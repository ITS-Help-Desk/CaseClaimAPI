from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from completeclaim.models import CompleteClaim
from completeclaim.serializers import CompleteClaimSerializer
from reviewedclaim.models import ReviewedClaim
from reviewedclaim.serializers import ReviewedClaimSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/review_complete_claim/<int:pk>/',
            'method': 'POST',
            'body': {'status': '', 'comment': ''},
            'description': 'Reviews a completed claim by creating a reviewed claim.'
        },
        {
            'Endpoint': '/list_complete_claims/',
            'method': 'GET',
            'body': None,
            'description': 'Lists all complete claims.'
        },
    ]
    return Response(routes)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def review_complete_claim(request, pk):
    try:
        claim = CompleteClaim.objects.get(pk=pk)
        tech = claim.user
        lead = request.user
        status_value = request.data.get('status')
        comment = request.data.get('comment', '')

        if not tech or not lead or not status_value:
            return Response({'error': 'Status are required fields'}, status=status.HTTP_400_BAD_REQUEST)

        new_claim = ReviewedClaim.objects.create(
            casenum=claim.casenum,
            tech=tech,
            lead=lead,
            claim_time=claim.claim_time,
            complete_time=claim.complete_time,
            status=status_value,
            comment=comment
        )

        claim.delete()

        serializer = ReviewedClaimSerializer(new_claim)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except CompleteClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_complete_claims(request):
    claims = CompleteClaim.objects.all()
    serializer = CompleteClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
