from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User, Group
from rest_framework import serializers

from .models import UserProfile


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['discord_id', 'must_reset_password', 'migrated_at']
        read_only_fields = ['migrated_at']


class UserSerializer(ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    discord_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    must_reset_password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'groups', 'discord_id', 'must_reset_password']
    
    def get_must_reset_password(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.must_reset_password
        return False
    
    def create(self, validated_data):
        discord_id = validated_data.pop('discord_id', None)
        user = super().create(validated_data)
        
        # Create profile with discord_id if provided
        UserProfile.objects.create(user=user, discord_id=discord_id)
        
        return user
