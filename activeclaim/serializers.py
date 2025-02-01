from rest_framework import serializers
from activeclaim.models import ActiveClaim


class ActiveClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveClaim
        fields = '__all__'