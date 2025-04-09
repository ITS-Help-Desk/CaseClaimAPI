from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from user.decorators import group_required

from activeclaim.models import ActiveClaim
from activeclaim.serializers import ActiveClaimSerializer
from completeclaim.models import CompleteClaim
from completeclaim.serializers import CompleteClaimSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/create_active_claim/<str:pk>/',
            'method': 'POST',
            'body': {'casenum': ''},
            'description': 'Creates a new active claim if the case number does not already exist.'
        },
        {
            'Endpoint': '/complete_active_claim/<str:pk>/',
            'method': 'DELETE',
            'body': None,
            'description': 'Marks an active claim as complete and moves it to the complete claims table.'
        },
        {
            'Endpoint': '/list_active_claims/',
            'method': 'GET',
            'body': None,
            'description': 'Lists all active claims.'
        },
    ]
    return Response(routes)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@group_required('Tech')
def create_active_claim(request, pk):
    if ActiveClaim.objects.filter(casenum=pk).exists():
        return Response("Casenum already exists.", status=400)
    
    claim = ActiveClaim.objects.create(user_id=request.user, casenum=pk)

    serializer = ActiveClaimSerializer(claim)

    return Response(serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@group_required('Tech')
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
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@group_required('Tech')
def list_active_claims(request):
    claims = ActiveClaim.objects.all()
    serializer = ActiveClaimSerializer(claims, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
