from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
            'Endpoint': '/create/<str:pk>/',
            'method': 'POST',
            'body': {'casenum': ''},
            'description': 'Creates a new active claim if the case number does not already exist.'
        },
        {
            'Endpoint': '/complete/<str:pk>/',
            'method': 'DELETE',
            'body': None,
            'description': 'Marks an active claim as complete and moves it to the complete claims table.'
        },
        {
            'Endpoint': '/unclaim/<str:pk>/',
            'method': 'DELETE',
            'body': None,
            'description': 'Deletes the active claim from the database.'
        },
        {
            'Endpoint': '/list/',
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

    # Notify WebSocket
    async_to_sync(get_channel_layer().group_send)(
        "caseflow",
        {
            "type": "activeclaim",
            "event": "claim",
            "casenum": claim.casenum,
            "user": claim.user_id.username
        }
    )

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
            user_id=claim.user_id,
            claim_time=claim.claim_time
        )
        claim.delete()

        serializer = CompleteClaimSerializer(new_claim)

        # Notify WebSocket
        async_to_sync(get_channel_layer().group_send)(
            "caseflow",
            {
                "type": "activeclaim",
                "event": "complete",
                "casenum": claim.casenum,
                "user": claim.user_id.username
            }
        )

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

@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def unclaim_active_claim(request, pk):
    try:
        claim = ActiveClaim.objects.get(casenum=pk)

        # Check permissions: Leads can unclaim any, Techs can only unclaim their own
        is_lead = request.user.groups.filter(name='Lead').exists()
        is_owner = claim.user_id == request.user

        if not (is_lead or is_owner):
            return Response({'error': 'Permission denied. You can only unclaim your own cases.'}, status=status.HTTP_403_FORBIDDEN)

        claim.delete()

        # Notify WebSocket
        async_to_sync(get_channel_layer().group_send)(
            "caseflow",
            {
                "type": "activeclaim",
                "event": "unclaimed",
                "casenum": claim.casenum,
                "user": claim.user_id.username
            }
        )

        return Response({'message': 'Claim successfully unclaimed.'}, status=status.HTTP_204_NO_CONTENT)
    except ActiveClaim.DoesNotExist:
        return Response({'error': 'Claim not found'}, status=status.HTTP_404_NOT_FOUND)
