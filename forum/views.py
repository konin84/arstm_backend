# apps/forum/views.py
from rest_framework import generics, permissions
from .models import Category, Topic, Post
from .serializers import CategoryForumSerializer, TopicSerializer, PostSerializer
from users.permissions import IsAdminOrModerator, IsAdminOrModeratorOrReadOnly


class CategoryListView(generics.ListCreateAPIView):
    """Lecture publique ; création réservée aux admins et modérateurs."""
    queryset = Category.objects.all()
    serializer_class = CategoryForumSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin/Modérateur : modifier ou supprimer une catégorie du forum."""
    queryset = Category.objects.all()
    serializer_class = CategoryForumSerializer
    permission_classes = [IsAdminOrModerator]


class TopicListCreateView(generics.ListCreateAPIView):
    """Lister les sujets d'une catégorie (Public) ou en créer un nouveau (Connecté)"""
    serializer_class = TopicSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Permet de filtrer les sujets par catégorie via l'URL ?category_id=1
        queryset = Topic.objects.all().order_by('-created_at')
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    def perform_create(self, serializer):
        # Assigne automatiquement l'utilisateur connecté comme auteur du sujet
        serializer.save(author=self.request.user)


class PostListCreateView(generics.ListCreateAPIView):
    """Afficher les discussions à l'intérieur d'un sujet (Public) ou y répondre (Connecté)"""
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Obligatoire : Filtrer pour n'avoir que les réponses du sujet en cours de consultation
        topic_id = self.request.query_params.get('topic_id')
        return Post.objects.filter(topic_id=topic_id).order_by('created_at')

    def perform_create(self, serializer):
        # Assigne automatiquement l'utilisateur connecté comme auteur du message
        serializer.save(author=self.request.user)


class TopicDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin/Modérateur : modifier ou supprimer un sujet (modération)."""
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAdminOrModerator]


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin/Modérateur : modifier ou supprimer un message (modération)."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminOrModerator]