from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from parentcase.models import ParentCase
from parentcase.serializers import ParentCaseSerializer

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_active_parent_cases(request):
    """
    Retrieve all active parent cases.

    Returns:
        Response: A JSON response containing serialized active parent cases with status 200.
    """
    cases = ParentCase.objects.filter(active=True)
    serializer = ParentCaseSerializer(cases, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_parent_cases(request):
    """
    Retrieve all parent cases, regardless of active status.

    Returns:
        Response: A JSON response containing serialized parent cases with status 200.
    """
    cases = ParentCase.objects.all()
    serializer = ParentCaseSerializer(cases, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def set_inactive_parent_case(request, case_num):
    """
    Set a specific parent case to inactive based on its case number.

    Args:
        case_num (str): The case number of the parent case to deactivate.

    Returns:
        Response: A JSON response with the updated parent case if successful,
                or an error message with appropriate status code if not.
    """
    try:
        case = ParentCase.objects.get(case_number=case_num)
        case.active = False
        case.save()
        serializer = ParentCaseSerializer(case)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ParentCase.DoesNotExist:
        return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Unable to update case'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_parent_case(request):
    """
    Create a new parent case with the provided data.

    Request Body:
        - case_number (str): The unique case number.
        - description (str): Description of the case.
        - solution (str): Optional solution associated with the case.

    Returns:
        Response: A JSON response with the created parent case data and status 201 if successful,
                or an error message with status 400 if creation fails.
    """
    try:
        solution = request.data.get('solution')
        created_case = ParentCase.objects.create(
            case_number = request.data.get('case_number'),
            description = request.data.get('description'),
            solution = solution,
            user = request.user
        )
        serialized = ParentCaseSerializer(created_case)
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': 'Unable to create parent case'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_parent_case(request, case_num):
    """
    Update an existing parent case identified by case number.

    Args:
        case_num (str): The case number of the parent case to update.

    Request Body:
        - description (str): Optional updated description.
        - solution (str): Optional updated solution.
        - active (bool): Optional status to set active/inactive.

    Returns:
        Response: A JSON response with the updated parent case data and status 200 if successful,
                or an error message with appropriate status code if update fails.
    """
    try:
        case = ParentCase.objects.get(case_number=case_num)
        if request.data.get('description') is not None:
            case.description = request.data.get('description')
        if request.data.get('solution') is not None:
            case.solution = request.data.get('solution')
        if 'active' in request.data:
            case.active = request.data.get('active')
        case.save()
        serializer = ParentCaseSerializer(case)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ParentCase.DoesNotExist:
        return Response({'error': 'Case not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Unable to update case'}, status=status.HTTP_400_BAD_REQUEST)