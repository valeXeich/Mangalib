from django.db.models import Max, Count
from rest_framework import viewsets, generics, views, mixins, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Comment, Manga, Genre, Page,  RatingComment, Tag, Rating, Chapter
from .serializers import (MangaListSerializer,
                          MangaDetailSerializer,
                          GenreSerializer,
                          MangaPopularSerializer, MangaNewSerializer,
                          MangaPopularNewChapters,
                          CommentSerializer,
                          TagSerializer,
                          MangaShortInfoSerializer,
                          CommentCreateSerializer,
                          CommentUpdateSerializer,
                          ChapterSerializer,
                          LatestChapterSerializer,
                          PageSerializer,
                          RatingSerializer,
                          VoteSerializer
                          )
from .paginations import MangaPagination
from .filters import MangaFilter


class MangaViewSet(viewsets.ModelViewSet):
    queryset = Manga.objects.all()
    serializer_class = MangaListSerializer
    lookup_field = 'slug'
    pagination_class = MangaPagination
    filterset_class = MangaFilter
    filter_backends = [filters.SearchFilter,
                       filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["ratings__star", "created_at", "chapters__created_at",
                       "chapters_count", "view_count", "ratings_count"]
    search_fields = ['title', 'subtitle']

    def get_serializer_class(self):
        if self.action == "list":
            return MangaListSerializer
        return MangaDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(ratings_count=Count("ratings"))
        queryset = queryset.annotate(chapters_count=Count("chapters"))
        return queryset

    @action(detail=True, methods=['get'])
    def chapters(self, request, slug):
        manga = self.get_object()
        chapters = manga.chapters.all()
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def short_info(self, request, slug):
        manga = self.get_object()
        serializer = MangaShortInfoSerializer(manga)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular_manga(self, request):
        queryset = self.get_queryset().order_by('-view_count')[:10]
        serializer = MangaPopularSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_manga(self, request):
        queryset = self.get_queryset().order_by('-created_at')[:10]
        serializer = MangaNewSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular_manga_chapters(self, request):
        queryset = self.get_queryset().annotate(
            latest_chapter_date=Max('chapters__created_at')
        ).order_by('-view_count', '-latest_chapter_date')[:6]
        serializer = MangaPopularNewChapters(queryset, many=True)
        return Response(serializer.data)


class ChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer

    @action(detail=True, methods=['get'])
    def pages(self, request, pk=None):
        chapter = self.get_object()
        pages = Page.objects.filter(chapter=chapter).order_by('page_number')
        serializer = PageSerializer(pages, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def latest(self, request):
        latest_chapters = Chapter.objects.order_by('-created_at')[:50]
        serializer = LatestChapterSerializer(latest_chapters, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_parent=False)
    serializer_class = CommentSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "ratings__vote"]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        elif self.action == 'update':
            return CommentUpdateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        manga_slug = self.request.query_params.get('manga')
        chapter_number = self.request.query_params.get('chapter')
        page_number = self.request.query_params.get('page')

        if manga_slug and page_number and chapter_number:
            queryset = queryset.filter(manga__slug=manga_slug, manga_page__page_number=page_number,
                                       manga_page__chapter__chapter_number=chapter_number)
        elif manga_slug:
            queryset = queryset.filter(
                manga__slug=manga_slug, is_page_comment=False)

        return queryset

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        user = request.user

        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        vote = serializer.validated_data['vote']

        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)

        comment_vote, created = RatingComment.objects.get_or_create(
            user=user, comment=comment, defaults={"vote": vote})

        if not created:
            if comment_vote.vote == vote:
                comment_vote.delete()
                return Response({'detail': 'Vote removed.'}, status=status.HTTP_200_OK)
            else:
                comment_vote.vote = vote
                comment_vote.save()
                return Response({'detail': 'Vote updated.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Vote added.'}, status=status.HTTP_201_CREATED)


class RatingViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        if Rating.objects.filter(manga=data['manga'], user=self.request.user).exists():
            return Response({'error': 'Rating for this manga already exists.'}, status=400)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def user_rating(self, request, manga_pk=None):
        try:
            rating = Rating.objects.get(user=request.user, manga=manga_pk)
            serializer = RatingSerializer(rating)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Rating.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class MangaTypeAPIView(views.APIView):

    def get(self, request):
        manga_types = ["Manga", "Manhwa", "Manhua"]
        return Response(manga_types)


class GenresListAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_queryset(self):
        limit = self.request.query_params.get('limit')
        if limit.isdigit():
            limit = int(limit)
            return super().get_queryset()[:limit]
        return super().get_queryset()


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
