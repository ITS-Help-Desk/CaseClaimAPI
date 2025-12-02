from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.db.models import Count, Q
from datetime import datetime

from user.decorators import role_required

from .models import Evaluation
from .serializers import EvaluationSerializer
from reviewedclaim.models import ReviewedClaim


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/create/',
            'method': 'POST',
            'body': {
                'tech': 'user_id',
                'period_start': 'YYYY-MM-DD',
                'period_end': 'YYYY-MM-DD',
                'strengths': 'text',
                'areas_for_improvement': 'text',
                'additional_comments': 'text',
                'overall_rating': '1-5'
            },
            'description': 'Create a new evaluation for a tech.'
        },
        {
            'Endpoint': '/list/',
            'method': 'GET',
            'body': None,
            'description': 'List all evaluations.'
        },
        {
            'Endpoint': '/user/<int:user_id>/',
            'method': 'GET',
            'body': None,
            'description': 'Get all evaluations for a specific user.'
        },
        {
            'Endpoint': '/detail/<int:pk>/',
            'method': 'GET',
            'body': None,
            'description': 'Get details of a specific evaluation.'
        },
        {
            'Endpoint': '/update/<int:pk>/',
            'method': 'PUT',
            'body': 'Same as create',
            'description': 'Update an existing evaluation.'
        },
        {
            'Endpoint': '/delete/<int:pk>/',
            'method': 'DELETE',
            'body': None,
            'description': 'Delete an evaluation.'
        },
        {
            'Endpoint': '/generate/<int:user_id>/',
            'method': 'GET',
            'query_params': {'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'},
            'description': 'Generate evaluation data/metrics for a user (does not save, just calculates).'
        },
    ]
    return Response(routes)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def create_evaluation(request):
    """
    Create a new evaluation for a tech.
    
    The evaluator is automatically set to the current user.
    """
    serializer = EvaluationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Set the evaluator to the current user
        serializer.save(evaluator=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def list_evaluations(request):
    """
    List all evaluations.
    
    Supports filtering by query params:
        - tech_id: Filter by tech user ID
        - evaluator_id: Filter by evaluator user ID
    """
    evaluations = Evaluation.objects.all()
    
    # Apply filters
    tech_id = request.query_params.get('tech_id')
    evaluator_id = request.query_params.get('evaluator_id')
    
    if tech_id:
        evaluations = evaluations.filter(tech_id=tech_id)
    if evaluator_id:
        evaluations = evaluations.filter(evaluator_id=evaluator_id)
    
    serializer = EvaluationSerializer(evaluations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_user_evaluations(request, user_id):
    """
    Get all evaluations for a specific user (as tech).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    evaluations = Evaluation.objects.filter(tech=user)
    serializer = EvaluationSerializer(evaluations, many=True)
    
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username
        },
        'evaluations': serializer.data,
        'total_count': evaluations.count()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_evaluation_detail(request, pk):
    """
    Get details of a specific evaluation.
    """
    try:
        evaluation = Evaluation.objects.get(pk=pk)
    except Evaluation.DoesNotExist:
        return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = EvaluationSerializer(evaluation)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def update_evaluation(request, pk):
    """
    Update an existing evaluation.
    """
    try:
        evaluation = Evaluation.objects.get(pk=pk)
    except Evaluation.DoesNotExist:
        return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Only the original evaluator or a Manager can update
    from user.decorators import get_user_highest_role_level, ROLE_HIERARCHY
    user_level = get_user_highest_role_level(request.user)
    manager_level = ROLE_HIERARCHY.get('Manager', 0)
    
    if evaluation.evaluator != request.user and user_level < manager_level:
        return Response(
            {'error': 'You can only update your own evaluations.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    partial = request.method == 'PATCH'
    serializer = EvaluationSerializer(evaluation, data=request.data, partial=partial)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def delete_evaluation(request, pk):
    """
    Delete an evaluation.
    """
    try:
        evaluation = Evaluation.objects.get(pk=pk)
    except Evaluation.DoesNotExist:
        return Response({'error': 'Evaluation not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Only the original evaluator or a Manager can delete
    from user.decorators import get_user_highest_role_level, ROLE_HIERARCHY
    user_level = get_user_highest_role_level(request.user)
    manager_level = ROLE_HIERARCHY.get('Manager', 0)
    
    if evaluation.evaluator != request.user and user_level < manager_level:
        return Response(
            {'error': 'You can only delete your own evaluations.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    evaluation.delete()
    return Response({'message': 'Evaluation deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def generate_evaluation_data(request, user_id):
    """
    Generate evaluation metrics/data for a user based on their case history.
    
    This does NOT create an evaluation - it just calculates the metrics
    that can be used to fill in an evaluation form.
    
    Query params:
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get date range from query params
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    
    if not start_date_str or not end_date_str:
        return Response({
            'error': 'Both start_date and end_date are required (YYYY-MM-DD format)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        return Response({
            'error': 'Invalid date format. Use YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get all reviewed claims for this tech in the date range
    reviewed_claims = ReviewedClaim.objects.filter(
        tech_id=user,
        review_time__gte=start_date,
        review_time__lte=end_date
    )
    
    total_cases = reviewed_claims.count()
    
    # Count by status
    kudos_count = reviewed_claims.filter(status='kudos').count()
    checked_count = reviewed_claims.filter(status='checked').count()
    done_count = reviewed_claims.filter(status='done').count()
    
    ping_statuses = ['pingedlow', 'pingedmed', 'pingedhigh', 'acknowledged', 'resolved']
    ping_count = reviewed_claims.filter(status__in=ping_statuses).count()
    
    # Calculate quality score (simple formula: (positive / total) * 100)
    positive_reviews = kudos_count + checked_count + done_count
    quality_score = round((positive_reviews / total_cases * 100), 2) if total_cases > 0 else None
    
    # Calculate ping rate
    ping_rate = round((ping_count / total_cases * 100), 2) if total_cases > 0 else 0
    
    evaluation_data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username
        },
        'period': {
            'start_date': start_date_str,
            'end_date': end_date_str
        },
        'metrics': {
            'cases_reviewed': total_cases,
            'quality_score': quality_score,
            'ping_count': ping_count,
            'ping_rate': ping_rate,
            'kudos_count': kudos_count,
        },
        'breakdown': {
            'kudos': kudos_count,
            'checked': checked_count,
            'done': done_count,
            'pinged_low': reviewed_claims.filter(status='pingedlow').count(),
            'pinged_med': reviewed_claims.filter(status='pingedmed').count(),
            'pinged_high': reviewed_claims.filter(status='pingedhigh').count(),
            'acknowledged': reviewed_claims.filter(status='acknowledged').count(),
            'resolved': reviewed_claims.filter(status='resolved').count(),
        },
        'suggested_rating': _calculate_suggested_rating(quality_score, ping_rate),
    }
    
    return Response(evaluation_data, status=status.HTTP_200_OK)


def _calculate_suggested_rating(quality_score, ping_rate):
    """
    Calculate a suggested rating based on metrics.
    
    This is just a suggestion - the lead can override it.
    """
    if quality_score is None:
        return None
    
    if quality_score >= 95 and ping_rate < 5:
        return 5  # Outstanding
    elif quality_score >= 85 and ping_rate < 10:
        return 4  # Exceeds Expectations
    elif quality_score >= 70 and ping_rate < 20:
        return 3  # Meets Expectations
    elif quality_score >= 50:
        return 2  # Below Expectations
    else:
        return 1  # Needs Improvement

