from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Author, Post, Comment, Like


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    def check_user(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid credentials')
        return user

class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = Author
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True}}

    def create(self, validated_data):
        author = Author.objects.create(
            email=validated_data['email'],
            display_name=validated_data['display_name'],
            github=validated_data['github'],
            profile_image=validated_data['profile_image']
        )
        author.set_password(validated_data['password'])
        author.save()

        return author


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

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'type', 'id', 'title', 'source', 'origin', 'description', 'contentType',
            'content', 'author', 'count', 'comments', 'published',
            'visibility', 'image'
        ]
        read_only_fields = ['type', 'id', 'author', 'count', 'comments', 'published']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        current_url = request.build_absolute_uri()
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        data["id"] = f"{current_url}{instance.id}"
        data["comments"] = f"{current_url}/{instance.id}/comments"
        return data
    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['type', 'id', 'author', 'comment', 'contentType', 'published', 'post']
        read_only_fields = ['type', 'id', 'author', 'published', 'post']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        current_url = request.build_absolute_uri()
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        data["id"] = f"{current_url}{instance.id}"
        return data
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = [ 'type', 'summary', 'author', 'post', 'comment']
        read_only_fields = ['type', 'author']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        if instance.comment:
            data["object"] = instance.comment.id
        elif instance.post:
            data["object"] = instance.post.id
        else:
            data["object"] = None
        return data