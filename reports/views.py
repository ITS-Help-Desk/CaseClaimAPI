from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from user.decorators import role_required

from activeclaim.models import ActiveClaim
from completeclaim.models import CompleteClaim
from reviewedclaim.models import ReviewedClaim


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/summary/',
            'method': 'GET',
            'body': None,
            'description': 'Get overall system statistics (total cases, completion rates, etc.).'
        },
        {
            'Endpoint': '/user/<int:user_id>/',
            'method': 'GET',
            'body': None,
            'description': 'Get statistics for a specific user.'
        },
        {
            'Endpoint': '/leaderboard/',
            'method': 'GET',
            'body': None,
            'description': 'Get leaderboard ranking of top performers.'
        },
        {
            'Endpoint': '/ping-stats/',
            'method': 'GET',
            'body': None,
            'description': 'Get statistics about pings (feedback given to techs).'
        },
        {
            'Endpoint': '/date-range/',
            'method': 'GET',
            'query_params': {'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'},
            'description': 'Get statistics filtered by date range.'
        },
    ]
    return Response(routes)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_summary(request):
    """
    Get overall system statistics.
    
    Returns counts and metrics across all case stages.
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    summary = {
        'generated_at': now,
        'totals': {
            'active_claims': ActiveClaim.objects.count(),
            'pending_review': CompleteClaim.objects.count(),
            'reviewed_claims': ReviewedClaim.objects.count(),
        },
        'today': {
            'claimed': ActiveClaim.objects.filter(claim_time__gte=today_start).count(),
            'completed': CompleteClaim.objects.filter(complete_time__gte=today_start).count(),
            'reviewed': ReviewedClaim.objects.filter(review_time__gte=today_start).count(),
        },
        'this_week': {
            'claimed': ActiveClaim.objects.filter(claim_time__gte=week_start).count(),
            'completed': CompleteClaim.objects.filter(complete_time__gte=week_start).count(),
            'reviewed': ReviewedClaim.objects.filter(review_time__gte=week_start).count(),
        },
        'review_status_breakdown': {
            'kudos': ReviewedClaim.objects.filter(status='kudos').count(),
            'checked': ReviewedClaim.objects.filter(status='checked').count(),
            'done': ReviewedClaim.objects.filter(status='done').count(),
            'pinged_low': ReviewedClaim.objects.filter(status='pingedlow').count(),
            'pinged_med': ReviewedClaim.objects.filter(status='pingedmed').count(),
            'pinged_high': ReviewedClaim.objects.filter(status='pingedhigh').count(),
            'acknowledged': ReviewedClaim.objects.filter(status='acknowledged').count(),
            'resolved': ReviewedClaim.objects.filter(status='resolved').count(),
        }
    }
    
    # Calculate ping rate
    total_reviewed = summary['totals']['reviewed_claims']
    total_pinged = (summary['review_status_breakdown']['pinged_low'] + 
                    summary['review_status_breakdown']['pinged_med'] + 
                    summary['review_status_breakdown']['pinged_high'] +
                    summary['review_status_breakdown']['acknowledged'] +
                    summary['review_status_breakdown']['resolved'])
    
    summary['ping_rate'] = round((total_pinged / total_reviewed * 100), 2) if total_reviewed > 0 else 0
    
    return Response(summary, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_user_stats(request, user_id):
    """
    Get statistics for a specific user.
    
    Shows their case counts, ping rates, and performance metrics.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    # Get user's cases as tech
    user_reviewed = ReviewedClaim.objects.filter(tech_id=user)
    
    # Count pings received
    pings_received = user_reviewed.filter(
        status__in=['pingedlow', 'pingedmed', 'pingedhigh', 'acknowledged', 'resolved']
    ).count()
    
    # Count positive reviews
    positive_reviews = user_reviewed.filter(
        status__in=['kudos', 'checked', 'done']
    ).count()
    
    total_reviews = user_reviewed.count()
    
    stats = {
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': f'{user.first_name} {user.last_name}'.strip() or user.username,
        },
        'as_tech': {
            'active_claims': ActiveClaim.objects.filter(user_id=user).count(),
            'completed_pending_review': CompleteClaim.objects.filter(user_id=user).count(),
            'total_reviewed': total_reviews,
            'positive_reviews': positive_reviews,
            'pings_received': pings_received,
            'ping_rate': round((pings_received / total_reviews * 100), 2) if total_reviews > 0 else 0,
        },
        'as_lead': {
            'reviews_given': ReviewedClaim.objects.filter(lead_id=user).count(),
            'reviews_today': ReviewedClaim.objects.filter(lead_id=user, review_time__gte=today_start).count(),
            'reviews_this_week': ReviewedClaim.objects.filter(lead_id=user, review_time__gte=week_start).count(),
        },
        'this_week': {
            'claimed': ActiveClaim.objects.filter(user_id=user, claim_time__gte=week_start).count(),
            'reviewed': user_reviewed.filter(review_time__gte=week_start).count(),
        },
        'this_month': {
            'reviewed': user_reviewed.filter(review_time__gte=month_start).count(),
        }
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_leaderboard(request):
    """
    Get leaderboard ranking of top performers.
    
    Ranks users by number of cases completed (reviewed).
    """
    # Get time range from query params (default: last 7 days)
    days = int(request.query_params.get('days', 7))
    limit = int(request.query_params.get('limit', 10))
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Get tech leaderboard (by cases completed)
    tech_stats = (
        ReviewedClaim.objects
        .filter(review_time__gte=start_date)
        .values('tech_id', 'tech_id__username', 'tech_id__first_name', 'tech_id__last_name')
        .annotate(
            total_cases=Count('id'),
            kudos=Count('id', filter=Q(status='kudos')),
            pings=Count('id', filter=Q(status__in=['pingedlow', 'pingedmed', 'pingedhigh']))
        )
        .order_by('-total_cases')[:limit]
    )
    
    # Get lead leaderboard (by reviews given)
    lead_stats = (
        ReviewedClaim.objects
        .filter(review_time__gte=start_date)
        .values('lead_id', 'lead_id__username', 'lead_id__first_name', 'lead_id__last_name')
        .annotate(reviews_given=Count('id'))
        .order_by('-reviews_given')[:limit]
    )
    
    leaderboard = {
        'period': f'Last {days} days',
        'generated_at': timezone.now(),
        'tech_leaderboard': [
            {
                'rank': idx + 1,
                'user_id': entry['tech_id'],
                'username': entry['tech_id__username'],
                'name': f"{entry['tech_id__first_name']} {entry['tech_id__last_name']}".strip() or entry['tech_id__username'],
                'total_cases': entry['total_cases'],
                'kudos': entry['kudos'],
                'pings': entry['pings'],
            }
            for idx, entry in enumerate(tech_stats)
        ],
        'lead_leaderboard': [
            {
                'rank': idx + 1,
                'user_id': entry['lead_id'],
                'username': entry['lead_id__username'],
                'name': f"{entry['lead_id__first_name']} {entry['lead_id__last_name']}".strip() or entry['lead_id__username'],
                'reviews_given': entry['reviews_given'],
            }
            for idx, entry in enumerate(lead_stats)
        ]
    }
    
    return Response(leaderboard, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_ping_stats(request):
    """
    Get statistics about pings (feedback given to techs).
    
    Shows ping counts by severity, resolution rates, etc.
    """
    now = timezone.now()
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    ping_statuses = ['pingedlow', 'pingedmed', 'pingedhigh', 'acknowledged', 'resolved']
    
    all_pings = ReviewedClaim.objects.filter(status__in=ping_statuses)
    active_pings = all_pings.filter(status__in=['pingedlow', 'pingedmed', 'pingedhigh'])
    acknowledged_pings = all_pings.filter(status='acknowledged')
    resolved_pings = all_pings.filter(status='resolved')
    
    stats = {
        'generated_at': now,
        'totals': {
            'all_pings': all_pings.count(),
            'active': active_pings.count(),
            'acknowledged': acknowledged_pings.count(),
            'resolved': resolved_pings.count(),
        },
        'by_severity': {
            'low': ReviewedClaim.objects.filter(status='pingedlow').count(),
            'medium': ReviewedClaim.objects.filter(status='pingedmed').count(),
            'high': ReviewedClaim.objects.filter(status='pingedhigh').count(),
        },
        'this_week': {
            'new_pings': all_pings.filter(review_time__gte=week_start).count(),
            'resolved': resolved_pings.filter(review_time__gte=week_start).count(),
        },
        'this_month': {
            'new_pings': all_pings.filter(review_time__gte=month_start).count(),
            'resolved': resolved_pings.filter(review_time__gte=month_start).count(),
        },
        'resolution_rate': round(
            (resolved_pings.count() / all_pings.count() * 100), 2
        ) if all_pings.count() > 0 else 0,
        
        # Top pinged techs
        'top_pinged_techs': list(
            all_pings
            .values('tech_id', 'tech_id__username')
            .annotate(ping_count=Count('id'))
            .order_by('-ping_count')[:5]
        )
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_date_range_stats(request):
    """
    Get statistics filtered by date range.
    
    Query params:
        - start_date: YYYY-MM-DD
        - end_date: YYYY-MM-DD
    """
    from datetime import datetime
    
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    
    if not start_date_str or not end_date_str:
        return Response({
            'error': 'Both start_date and end_date are required (YYYY-MM-DD format)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Make end_date inclusive by going to end of day
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        return Response({
            'error': 'Invalid date format. Use YYYY-MM-DD'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get stats for the date range
    reviewed_in_range = ReviewedClaim.objects.filter(
        review_time__gte=start_date,
        review_time__lte=end_date
    )
    
    stats = {
        'date_range': {
            'start': start_date_str,
            'end': end_date_str,
        },
        'totals': {
            'cases_reviewed': reviewed_in_range.count(),
        },
        'by_status': {
            'kudos': reviewed_in_range.filter(status='kudos').count(),
            'checked': reviewed_in_range.filter(status='checked').count(),
            'done': reviewed_in_range.filter(status='done').count(),
            'pinged_low': reviewed_in_range.filter(status='pingedlow').count(),
            'pinged_med': reviewed_in_range.filter(status='pingedmed').count(),
            'pinged_high': reviewed_in_range.filter(status='pingedhigh').count(),
        },
        'top_techs': list(
            reviewed_in_range
            .values('tech_id', 'tech_id__username')
            .annotate(case_count=Count('id'))
            .order_by('-case_count')[:10]
        ),
        'top_leads': list(
            reviewed_in_range
            .values('lead_id', 'lead_id__username')
            .annotate(review_count=Count('id'))
            .order_by('-review_count')[:10]
        )
    }
    
    return Response(stats, status=status.HTTP_200_OK)

