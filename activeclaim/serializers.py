from rest_framework import serializers
from activeclaim.models import ActiveClaim


class ActiveClaimSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = ActiveClaim
        fields = '__all__'
    
    def get_user_name(self, obj):
        return obj.user_id.username if obj.user_id else None
    
    def get_full_name(self, obj):
        if obj.user_id:
            return f"{obj.user_id.first_name} {obj.user_id.last_name}".strip()
        return None