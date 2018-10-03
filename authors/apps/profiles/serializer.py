from rest_framework import serializers
from .models import Profile
from django.db.models import ImageField


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializes and deserializes Profile instances.
    """
    # Fields from the user model
    username = serializers.CharField(source='user.username', read_only=True)
    # Profile specific fields
    bio = serializers.CharField()
    image = ImageField()

    class Meta:
        model = Profile
        fields = ['username', 'bio', 'image_url']
