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
        data['id'] = f"{request.build_absolute_uri('/api/authors/')}{instance.id}"
        return data

    def get_url(self, obj):
        request = self.context.get('request')
        url = f"{request.build_absolute_uri('/api/authors/')}{obj.id}"
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
            'visibility', 'image', 'image_url', 'sharedBy'
        ]
        read_only_fields = ['type', 'id', 'author', 'count', 'comments', 'published']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        data["author"] = AuthorSerializer(instance.author, context=self.context).data
        current_url = f"{request.build_absolute_uri('/')}api/authors/{instance.author.id}/posts"
        data['id'] = f"{current_url}/{instance.id}"
        data["comments"] = f"{current_url}/{instance.id}/comments"
        if (not data['image']) and (data['image_url']):
            data['image'] = data['image_url']
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
        data["post"] = PostSerializer(instance.post, context=self.context).data
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
                data['summary'] = f"{instance.author.displayName} liked the comment"
        elif instance.post:
            if data['object'] == None or data['object'] == '':
                data["object"] = f"{request.build_absolute_uri('/')}api/authors/{instance.post.author.id}/posts/{instance.post.id}"
            if data['summary'] == None or data['summary'] == '':
                data['summary'] = f"{instance.author.displayName} liked the post"
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