from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from user.decorators import role_required

from activeclaim.models import ActiveClaim
from activeclaim.serializers import ActiveClaimSerializer
from completeclaim.models import CompleteClaim
from completeclaim.serializers import CompleteClaimSerializer
from reviewedclaim.models import ReviewedClaim
from reviewedclaim.serializers import ReviewedClaimSerializer


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/search/<str:casenum>/',
            'method': 'GET',
            'body': None,
            'description': 'Search for a case across all tables and return its current state.'
        },
        {
            'Endpoint': '/history/<str:casenum>/',
            'method': 'GET',
            'body': None,
            'description': 'Get the complete history/timeline of a case.'
        },
        {
            'Endpoint': '/status/<str:casenum>/',
            'method': 'GET',
            'body': None,
            'description': 'Get a quick status check for a case (active/complete/reviewed/not found).'
        },
    ]
    return Response(routes)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def search_case(request, casenum):
    """
    Search for a case across all tables and return its current state with full details.
    
    Returns:
        - The case data from whichever table it currently exists in
        - The current status (active, complete, reviewed)
        - Any associated data (user info, timestamps, etc.)
    """
    result = {
        'casenum': casenum,
        'found': False,
        'current_status': None,
        'data': None
    }
    
    # Check ActiveClaim first (currently being worked on)
    try:
        active_claim = ActiveClaim.objects.get(casenum=casenum)
        result['found'] = True
        result['current_status'] = 'active'
        result['data'] = ActiveClaimSerializer(active_claim).data
        return Response(result, status=status.HTTP_200_OK)
    except ActiveClaim.DoesNotExist:
        pass
    
    # Check CompleteClaim (completed, awaiting review)
    try:
        complete_claim = CompleteClaim.objects.get(casenum=casenum)
        result['found'] = True
        result['current_status'] = 'complete'
        result['data'] = CompleteClaimSerializer(complete_claim).data
        return Response(result, status=status.HTTP_200_OK)
    except CompleteClaim.DoesNotExist:
        pass
    
    # Check ReviewedClaim (already reviewed - may have multiple entries)
    reviewed_claims = ReviewedClaim.objects.filter(casenum=casenum).order_by('-review_time')
    if reviewed_claims.exists():
        result['found'] = True
        result['current_status'] = 'reviewed'
        # Return the most recent review, but include count of all reviews
        result['data'] = ReviewedClaimSerializer(reviewed_claims.first()).data
        result['total_reviews'] = reviewed_claims.count()
        return Response(result, status=status.HTTP_200_OK)
    
    # Case not found in any table
    return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_case_history(request, casenum):
    """
    Get the complete history/timeline of a case across all stages.
    
    Returns a timeline showing when the case moved through each stage.
    """
    history = {
        'casenum': casenum,
        'timeline': []
    }
    
    # Check if currently active
    try:
        active_claim = ActiveClaim.objects.get(casenum=casenum)
        history['timeline'].append({
            'stage': 'active',
            'status': 'current',
            'claimed_by': active_claim.user_id.username if active_claim.user_id else None,
            'claim_time': active_claim.claim_time,
            'data': ActiveClaimSerializer(active_claim).data
        })
    except ActiveClaim.DoesNotExist:
        pass
    
    # Check if in complete stage
    try:
        complete_claim = CompleteClaim.objects.get(casenum=casenum)
        history['timeline'].append({
            'stage': 'complete',
            'status': 'current',
            'completed_by': complete_claim.user_id.username if complete_claim.user_id else None,
            'claim_time': complete_claim.claim_time,
            'complete_time': complete_claim.complete_time,
            'reviewing_lead': complete_claim.lead_id.username if complete_claim.lead_id else None,
            'data': CompleteClaimSerializer(complete_claim).data
        })
    except CompleteClaim.DoesNotExist:
        pass
    
    # Get all reviewed entries (there may be multiple if case was pinged multiple times)
    reviewed_claims = ReviewedClaim.objects.filter(casenum=casenum).order_by('review_time')
    for review in reviewed_claims:
        history['timeline'].append({
            'stage': 'reviewed',
            'status': review.status,
            'tech': review.tech_id.username if review.tech_id else None,
            'lead': review.lead_id.username if review.lead_id else None,
            'claim_time': review.claim_time,
            'complete_time': review.complete_time,
            'review_time': review.review_time,
            'comment': review.comment,
            'data': ReviewedClaimSerializer(review).data
        })
    
    if not history['timeline']:
        return Response({
            'casenum': casenum,
            'error': 'Case not found in any stage'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(history, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
@role_required('Lead')  # Lead and above only
def get_case_status(request, casenum):
    """
    Quick status check for a case.
    
    Returns just the current stage and basic info.
    """
    # Check ActiveClaim
    if ActiveClaim.objects.filter(casenum=casenum).exists():
        claim = ActiveClaim.objects.get(casenum=casenum)
        return Response({
            'casenum': casenum,
            'status': 'active',
            'message': f'Case is currently active, claimed by {claim.user_id.username if claim.user_id else "unknown"}'
        }, status=status.HTTP_200_OK)
    
    # Check CompleteClaim
    if CompleteClaim.objects.filter(casenum=casenum).exists():
        claim = CompleteClaim.objects.get(casenum=casenum)
        reviewing = f', being reviewed by {claim.lead_id.username}' if claim.lead_id else ''
        return Response({
            'casenum': casenum,
            'status': 'complete',
            'message': f'Case is completed, awaiting review{reviewing}'
        }, status=status.HTTP_200_OK)
    
    # Check ReviewedClaim
    reviewed = ReviewedClaim.objects.filter(casenum=casenum).order_by('-review_time').first()
    if reviewed:
        return Response({
            'casenum': casenum,
            'status': 'reviewed',
            'review_status': reviewed.status,
            'message': f'Case has been reviewed with status: {reviewed.status}'
        }, status=status.HTTP_200_OK)
    
    # Not found
    return Response({
        'casenum': casenum,
        'status': 'not_found',
        'message': 'Case not found in any stage'
    }, status=status.HTTP_404_NOT_FOUND)

