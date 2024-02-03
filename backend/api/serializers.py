from rest_framework import serializers
from .models import Author


class AuthorSerializer(serializers.Serializer):
    type = serializers.CharField(default="author", read_only=True)
    id = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField(source='get_url', read_only=True)
    host = serializers.SerializerMethodField(source='get_host', read_only=True)
    displayName = serializers.CharField(source='display_name')
    github = serializers.CharField()
    profileImage = serializers.CharField(source='profile_image')

    class Meta:
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

    def get_url(self, obj):
        request = self.context.get('request')
        url = f"{request.META.get('HTTP_REFERER')}{obj.id}"
        return url

    def get_host(self, obj):
        request = self.context.get('request')
        host = f"http://{request.META.get('HTTP_HOST')}/"
        return host
