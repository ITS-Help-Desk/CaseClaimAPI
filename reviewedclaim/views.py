from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from reviewedclaim.models import ReviewedClaim
from reviewedclaim.serializers import ReviewedClaimSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/list_reviewed_claims/',
            'method': 'GET',
            'body': None,
            'description': 'Lists all reviewed claims.'
        },
    ]
    return Response(routes)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_reviewed_claims(request):
    claims = ReviewedClaim.objects.all()
    serializer = ReviewedClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
