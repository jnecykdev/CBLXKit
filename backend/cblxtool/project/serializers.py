# project/serializers.py
from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'created_at', 'image', 'owner_id', 'owner_email']

class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('image',)

class ProjectMetaSerializer(serializers.ModelSerializer):
    collaborators = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "collaborators"]