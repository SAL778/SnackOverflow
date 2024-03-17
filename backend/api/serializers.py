from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Author, Post, Comment, Like, Inbox, FollowRequest


# Adapted from: https://github.com/dotja/authentication_app_react_django_rest/blob/main/backend/user_api/serializers.py
# Accessed 2024-02-22
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)


# Adapted from: https://github.com/dotja/authentication_app_react_django_rest/blob/main/backend/user_api/serializers.py
# Accessed 2024-02-22
class UserRegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = Author
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}, 'id': {'read_only': True}}

    def create(self, validated_data):
        # create() creates an entry in the database, so it calls .save() internally
        author = Author.objects.create(
            email=validated_data['email'],
            password=validated_data['password'],
            display_name=validated_data['display_name'],
            github=validated_data['github'],
            profile_image=validated_data['profile_image'],
        )

        # since this is only used by our frontend, we can get the host from the request and set the host field, and url field
        request = self.context.get('request')
        author.host = f"{request.build_absolute_uri('/')}"
        author.url = f"{request.build_absolute_uri('/api/authors/')}{author.id}"

        author.save()

        return author


class AuthorSerializer(serializers.ModelSerializer):
    displayName = serializers.CharField(source='display_name')
    profileImage = serializers.URLField(source='profile_image', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Author
        fields = ['type', 'id', 'host', 'displayName', 'url', 'github', 'profileImage']
        read_only_fields = ['type', 'id', 'url', 'host']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.url
        return data


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
    
    def create(self, obj):
        from_user_data = AuthorSerializer(obj.from_user, context=self.context).data.get('id')
        to_user_data = AuthorSerializer(obj.to_user, context=self.context).data.get('id')

        # Create FollowRequest instance
        follow_request = FollowRequest.objects.create(
            from_user=from_user_data,
            to_user=to_user_data
        )
        return follow_request


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
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        current_url = f"{request.build_absolute_uri('/')}api/authors/{instance.author.id}/posts"
        data['id'] = f"{current_url}/{instance.id}"
        data["comments"] = f"{current_url}/{instance.id}/comments"
        return data
    
class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ['type', 'id', 'author', 'comment', 'contentType', 'published', 'post']
        read_only_fields = ['type', 'id', 'published']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        current_url = f"{request.build_absolute_uri('/')}api/authors/{instance.post.author.id}/posts/{instance.post.id}/comments"
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        data["id"] = f"{current_url}/{instance.id}"
        return data

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = [ 'type', 'summary', 'author', 'post', 'comment', 'object']
        read_only_fields = ['type']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        request = self.context.get('request')
        if instance.comment:
            if data['object'] == None or data['object'] == '':
                data["object"] = f"{request.build_absolute_uri('/')}api/authors/{instance.post.author.id}/posts/{instance.post.id}/comments/{instance.comment.id}"
            if data['summary'] == None or data['summary'] == '':
                data['summary'] = f"{instance.author.display_name} liked the comment"
        elif instance.post:
            if data['object'] == None or data['object'] == '':
                data["object"] = f"{request.build_absolute_uri('/')}api/authors/{instance.post.author.id}/posts/{instance.post.id}"
            if data['summary'] == None or data['summary'] == '':
                data['summary'] = f"{instance.author.display_name} liked the post"
        else:
            data["object"] = None
        return data

class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inbox
        fields = ['author', 'item','published']
        read_only_fields = ['type', 'published']
    
    def to_representation(self, instance):
        # data = super().to_representation(instance)
        # data["item"] = instance.item
        # check if the item type is a post or a comment
        # if instance.item.get('type') == 'post':
        #     data["item"] = PostSerializer(instance.item, context=self.context).data
        # elif instance.item.get('type') == 'comment':
        #     data["item"] = CommentSerializer(instance.item, context=self.context).data
        # elif instance.item.get('type') == 'like':
        #     data["item"] = LikeSerializer(instance.item, context=self.context).data
        # elif instance.item.get('type') == 'follow':
        #     data["item"] = FollowRequestSerializer(instance.item, context=self.context).data
        # else:
        #     data["item"] = instance.item

        return instance.item