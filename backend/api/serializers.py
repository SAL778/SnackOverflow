from rest_framework import serializers
from .models import Author


class AuthorSerializer(serializers.Serializer):
    type = serializers.CharField(default="author", read_only=True)
    id = serializers.CharField(read_only=True)
    url = serializers.SerializerMethodField(source='get_url', read_only=True)
    host = serializers.SerializerMethodField(source='get_host', read_only=True)
    # only these fields can be updated (not read_only) on POST request:
    displayName = serializers.CharField(source='display_name')
    github = serializers.CharField()
    profileImage = serializers.CharField(source='profile_image')

    class Meta:
        fields = ['type', 'id', 'url', 'host', 'displayName', 'github', 'profileImage']

    def update(self, instance, validated_data):
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.github = validated_data.get('github', instance.github)
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        data['id'] = f"{request.build_absolute_uri('/authors/')}{instance.id}"
        return data

    def get_url(self, obj):
        request = self.context.get('request')
        url = f"{request.build_absolute_uri('/authors/')}{obj.id}"
        return url

    def get_host(self, obj):
        request = self.context.get('request')
        host = f"{request.build_absolute_uri('/')}"
        return host


class FollowRequestSerializer(serializers.Serializer):
    type = serializers.CharField(default="Follow", read_only=True)
    summary = serializers.SerializerMethodField()
    actor = serializers.SerializerMethodField()
    object = serializers.SerializerMethodField()

    class Meta:
        fields = ['type', 'summary', 'actor', 'object']

    def get_actor(self, obj):
        actor = AuthorSerializer(obj.from_user, context=self.context).data
        return actor

    def get_object(self, obj):
        object = AuthorSerializer(obj.to_user, context=self.context).data
        return object

    def get_summary(self, obj):
        return f'{obj.from_user.display_name} sent a follow request to {obj.to_user.display_name}'
