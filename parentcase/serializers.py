from rest_framework import serializers
from parentcase.models import ParentCase


class ParentCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentCase
        fields = '__all__'
