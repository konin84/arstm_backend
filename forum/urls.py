# apps/forum/urls.py
from django.urls import path
from .views import CategoryListView, TopicListCreateView, PostListCreateView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='forum_categories'),
    path('topics/', TopicListCreateView.as_view(), name='forum_topics'),
    path('posts/', PostListCreateView.as_view(), name='forum_posts'),
]