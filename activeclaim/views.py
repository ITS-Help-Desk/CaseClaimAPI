from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from activeclaim.models import ActiveClaim
from activeclaim.serializers import ActiveClaimSerializer
from completeclaim.models import CompleteClaim
from completeclaim.serializers import CompleteClaimSerializer


@api_view(['POST'])
def create_active_claim(request):
    serializer = ActiveClaimSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def complete_active_claim(request, pk):
    try:
        claim = ActiveClaim.objects.get(casenum=pk)
        new_claim = CompleteClaim.objects.create(
            casenum=claim.casenum,
            user=claim.user,
            claim_time=claim.claim_time
        )
        claim.delete()

        serializer = CompleteClaimSerializer(new_claim)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ActiveClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def list_active_claims(request):
    claims = ActiveClaim.objects.all()
    serializer = ActiveClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
