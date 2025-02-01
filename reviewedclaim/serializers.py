from rest_framework import serializers
from reviewedclaim.models import ReviewedClaim


class ReviewedClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewedClaim
        fields = '__all__'
