from rest_framework import serializers
from completeclaim.models import CompleteClaim


class CompleteClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompleteClaim
        fields = '__all__'
