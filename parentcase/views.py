from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from parentcase.models import ParentCase
from parentcase.serializers import ParentCaseSerializer

# Create your views here.
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_active_parent_cases(request):
    cases = ParentCase.objects.filter(active=True)
    serializer = ParentCaseSerializer(cases, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_parent_case(request):
    try:
        solution = None
        if request.data.get('solution'):
            solution = request.data.get('solution')
        created_case = ParentCase.objects.create(
            case_number = request.data.get('case_number'),
            description = request.data.get('description'),
            solution = solution,
            user = request.user
        )
        serialized = ParentCaseSerializer(created_case)
        return Response(serialized.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Unable to create parent case'}, status=status.HTTP_400_BAD_REQUEST)