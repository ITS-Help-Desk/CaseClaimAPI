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
    Get overall system statistics, optionally filtered by date range.
    
    Query params:
      - days=7 (filter reviewed claims to last N days)
      - start_date=YYYY-MM-DD&end_date=YYYY-MM-DD (exact range)
      - user_id=N (filter to specific user as tech)
    Without date params, returns all-time totals.
    """
    from datetime import datetime as dt
    
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    # Determine date range filter
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    days_param = request.query_params.get('days')
    user_id = request.query_params.get('user_id')
    
    reviewed_qs = ReviewedClaim.objects.all()
    active_qs = ActiveClaim.objects.all()
    complete_qs = CompleteClaim.objects.all()
    
    period_label = 'All Time'
    
    if start_date_str and end_date_str:
        try:
            range_start = timezone.make_aware(dt.strptime(start_date_str, '%Y-%m-%d'))
            range_end = timezone.make_aware(
                dt.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            )
            reviewed_qs = reviewed_qs.filter(review_time__gte=range_start, review_time__lte=range_end)
            active_qs = active_qs.filter(claim_time__gte=range_start, claim_time__lte=range_end)
            complete_qs = complete_qs.filter(complete_time__gte=range_start, complete_time__lte=range_end)
            period_label = f'{start_date_str} to {end_date_str}'
        except ValueError:
            pass
    elif days_param:
        days = int(days_param)
        range_start = now - timedelta(days=days)
        reviewed_qs = reviewed_qs.filter(review_time__gte=range_start)
        active_qs = active_qs.filter(claim_time__gte=range_start)
        complete_qs = complete_qs.filter(complete_time__gte=range_start)
        period_label = f'Last {days} days'
    
    if user_id:
        reviewed_qs = reviewed_qs.filter(tech_id=int(user_id))
        active_qs = active_qs.filter(user_id=int(user_id))
        complete_qs = complete_qs.filter(user_id=int(user_id))
    
    total_reviewed = reviewed_qs.count()
    
    review_breakdown = {
        'kudos': reviewed_qs.filter(status='kudos').count(),
        'checked': reviewed_qs.filter(status='checked').count(),
        'done': reviewed_qs.filter(status='done').count(),
        'pinged_low': reviewed_qs.filter(status='pingedlow').count(),
        'pinged_med': reviewed_qs.filter(status='pingedmed').count(),
        'pinged_high': reviewed_qs.filter(status='pingedhigh').count(),
        'acknowledged': reviewed_qs.filter(status='acknowledged').count(),
        'resolved': reviewed_qs.filter(status='resolved').count(),
    }
    
    total_pinged = (review_breakdown['pinged_low'] + 
                    review_breakdown['pinged_med'] + 
                    review_breakdown['pinged_high'] +
                    review_breakdown['acknowledged'] +
                    review_breakdown['resolved'])
    
    summary = {
        'generated_at': now,
        'period': period_label,
        'totals': {
            'active_claims': active_qs.count(),
            'pending_review': complete_qs.count(),
            'reviewed_claims': total_reviewed,
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
        'review_status_breakdown': review_breakdown,
        'ping_rate': round((total_pinged / total_reviewed * 100), 2) if total_reviewed > 0 else 0,
    }
    
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
    
    Supports flexible date filtering via query params:
      - days=7 (default, last N days)
      - start_date=YYYY-MM-DD&end_date=YYYY-MM-DD (exact range)
      - limit=10 (max results per board)
    """
    from datetime import datetime as dt
    
    limit = int(request.query_params.get('limit', 10))
    
    start_date_str = request.query_params.get('start_date')
    end_date_str = request.query_params.get('end_date')
    
    if start_date_str and end_date_str:
        try:
            start_date = timezone.make_aware(dt.strptime(start_date_str, '%Y-%m-%d'))
            end_date = timezone.make_aware(
                dt.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            )
            period_label = f'{start_date_str} to {end_date_str}'
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        period_label = f'Last {days} days'
    
    base_qs = ReviewedClaim.objects.filter(
        review_time__gte=start_date,
        review_time__lte=end_date
    )
    
    # Tech leaderboard: cases where tech got checked or kudos
    tech_stats = (
        base_qs
        .filter(status__in=['checked', 'kudos'])
        .values('tech_id', 'tech_id__username', 'tech_id__first_name', 'tech_id__last_name')
        .annotate(
            total_cases=Count('id'),
            kudos_count=Count('id', filter=Q(status='kudos')),
        )
        .order_by('-total_cases')[:limit]
    )
    
    # Lead leaderboard: all reviews given, with status breakdown
    lead_stats = (
        base_qs
        .values('lead_id', 'lead_id__username', 'lead_id__first_name', 'lead_id__last_name')
        .annotate(
            total_reviews=Count('id'),
            kudos_count=Count('id', filter=Q(status='kudos')),
            checks_count=Count('id', filter=Q(status='checked')),
            pings_count=Count('id', filter=Q(status__in=['pingedlow', 'pingedmed', 'pingedhigh'])),
            done_count=Count('id', filter=Q(status='done')),
        )
        .order_by('-total_reviews')[:limit]
    )
    
    leaderboard = {
        'period': period_label,
        'generated_at': timezone.now(),
        'tech_leaderboard': [
            {
                'rank': idx + 1,
                'id': entry['tech_id'],
                'username': f"{entry['tech_id__first_name']} {entry['tech_id__last_name']}".strip() or entry['tech_id__username'],
                'count': entry['total_cases'],
                'kudosCount': entry['kudos_count'],
            }
            for idx, entry in enumerate(tech_stats)
        ],
        'lead_leaderboard': [
            {
                'rank': idx + 1,
                'id': entry['lead_id'],
                'username': f"{entry['lead_id__first_name']} {entry['lead_id__last_name']}".strip() or entry['lead_id__username'],
                'count': entry['total_reviews'],
                'kudosCount': entry['kudos_count'],
                'checksCount': entry['checks_count'],
                'pingsCount': entry['pings_count'],
                'doneCount': entry['done_count'],
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

