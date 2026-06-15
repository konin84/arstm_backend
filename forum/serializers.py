# apps/forum/serializers.py
from rest_framework import serializers
from .models import Category, Topic, Post
from django.contrib.auth import get_user_model

User = get_user_model()

class UserForumSerializer(serializers.ModelSerializer):
    """Sérialiseur minimal pour afficher l'identité de l'auteur d'un message"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'role']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.email


class CategoryForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class PostSerializer(serializers.ModelSerializer):
    author_detail = UserForumSerializer(source='author', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'topic', 'author', 'author_detail', 'content', 'created_at']
        read_only_fields = ['author']


class TopicSerializer(serializers.ModelSerializer):
    author_detail = UserForumSerializer(source='author', read_only=True)
    # Champ calculé pour afficher le dynamisme d'un sujet sur le frontend
    posts_count = serializers.IntegerField(source='posts.count', read_only=True)

    class Meta:
        model = Topic
        fields = ['id', 'category', 'title', 'author', 'author_detail', 'posts_count', 'created_at']
        read_only_fields = ['author']