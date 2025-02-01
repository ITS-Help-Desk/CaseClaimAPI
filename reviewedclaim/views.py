from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from reviewedclaim.models import ReviewedClaim
from reviewedclaim.serializers import ReviewedClaimSerializer


@api_view(['GET'])
def list_reviewed_claims(request):
    claims = ReviewedClaim.objects.all()
    serializer = ReviewedClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
