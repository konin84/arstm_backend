# apps/forum/urls.py
from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    TopicListCreateView, TopicDetailView,
    PostListCreateView, PostDetailView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='forum_categories'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='forum_category_detail'),
    path('topics/', TopicListCreateView.as_view(), name='forum_topics'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='forum_topic_detail'),
    path('posts/', PostListCreateView.as_view(), name='forum_posts'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='forum_post_detail'),
]