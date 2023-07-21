from rest_framework import serializers

from .models import Manga, Comment, Chapter, Genre, Page, Tag, Rating


class GenreSerializer(serializers.ModelSerializer):
    total_manga = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ["id", "name", "total_manga"]

    def get_total_manga(self, obj):
        return obj.manga_set.count()


class TagSerializer(serializers.ModelSerializer):
    total_manga = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ["id", "name", "total_manga"]

    def get_total_manga(self, obj):
        return obj.manga_set.count()


class MangaPopularSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manga
        fields = ["title", "subtitle", "image", "view_count"]


class MangaNewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manga
        fields = ["title", "subtitle", "image"]


class MangaShortInfoSerializer(serializers.ModelSerializer):
    age_rating = serializers.CharField(source="get_age_rating_display")
    author = serializers.CharField(source="author.name")
    rating = serializers.FloatField(source="get_avg_rating")
    genres = GenreSerializer(many=True)
    tag = TagSerializer(many=True)

    class Meta:
        model = Manga
        fields = ["title", "subtitle", "description", "release_year",
                  "age_rating", "author", "rating", "genres", "tag"]


class MangaListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manga
        fields = ["id", "title", "image", "type", "slug"]


class MangaPopularNewChapters(serializers.ModelSerializer):
    last_chapter = serializers.SerializerMethodField()

    class Meta:
        model = Manga
        fields = ["title", "image", "last_chapter"]

    def get_last_chapter(self, obj):
        last_chapter = obj.chapters.last()
        if last_chapter:
            serializer = ChapterSerizaliser(last_chapter)
            return serializer.data
        return


class RelatedMangaSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = Manga
        fields = ["id", "title", "type", "status", "slug"]


class MangaDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    tag = TagSerializer(many=True)
    type = serializers.CharField(source="get_type_display")
    status = serializers.SerializerMethodField()
    author = serializers.CharField(source="author.name")
    age_rating = serializers.CharField(source="get_age_rating_display")
    painter = serializers.CharField(source="painter.name")
    related_manga = RelatedMangaSerializer(many=True)
    total_chapters = serializers.IntegerField(source="get_total_chapters")
    rating = serializers.FloatField(source="get_avg_rating")
    ratings = serializers.DictField(source="get_ratings")
    user_list = serializers.DictField(source="get_user_list")

    class Meta:
        model = Manga
        fields = [
            "id",
            "title",
            "subtitle",
            "description",
            "image",
            "backround_image",
            "genres",
            "type",
            "release_year",
            "related_manga",
            "status",
            "author",
            "painter",
            "age_rating",
            "total_chapters",
            "rating",
            "ratings",
            "user_list",
            "tag"
        ]

    def get_status(self, obj):
        status = obj.status
        status_display = obj.get_status_display()
        data = {"status": status, "status_display": status_display}
        return data
    

class ChapterSerizaliser(serializers.ModelSerializer):
    volume = serializers.IntegerField(source="volume.volume_number")

    class Meta:
        model = Chapter
        fields = ["id", "title", "volume", "chapter_number"]


class ChapterSerializer(serializers.ModelSerializer):
    volume_number = serializers.IntegerField(source='volume.volume_number')
    total_pages = serializers.IntegerField(source='pages.count')

    class Meta:
        model = Chapter
        fields = ["id", "volume_number",
                  "chapter_number", "title", "total_pages"]


class LatestChapterSerializer(serializers.ModelSerializer):
    volume_number = serializers.IntegerField(source='volume.volume_number')
    total_pages = serializers.IntegerField(source='pages.count')
    manga_title = serializers.CharField(source='manga.title')
    manga_subtitle = serializers.CharField(source='manga.subtitle')

    class Meta:
        model = Chapter
        fields = ["id", "volume_number", "chapter_number", "title",
                  "total_pages", "created_at", "manga_title", "manga_subtitle"]


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ["id", "image", "page_number"]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    author_image = serializers.URLField(source="author.avatar", read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "author", "author_image",
                  "created_at", "replies", "rating"]

    def get_replies(self, obj):
        replies = obj.replies.all()
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    def get_rating(self, obj):
        votes = obj.ratings.all()
        rating = sum(vote.vote for vote in votes)
        return rating


class CommentCreateSerializer(serializers.ModelSerializer):
    manga = serializers.PrimaryKeyRelatedField(
        queryset=Manga.objects.all(), required=True)
    manga_page = serializers.PrimaryKeyRelatedField(
        queryset=Page.objects.all(), required=False, allow_null=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), required=False, allow_null=True)
    is_page_comment = serializers.BooleanField(default=False, read_only=True)
    is_parent = serializers.BooleanField(default=False, read_only=True)

    class Meta:
        model = Comment
        fields = ["manga", "content", "manga_page",
                  "is_page_comment", "parent", "is_parent"]

    def create(self, validated_data):
        parent = validated_data.get('parent')
        if parent:
            validated_data['is_parent'] = True
            if parent.is_page_comment:
                validated_data['manga_page'] = parent.manga_page
        if validated_data.get('manga_page'):
            validated_data['is_page_comment'] = True
        return super().create(validated_data)

    def validate(self, attrs):
        page = attrs.get('manga_page')
        manga = attrs.get('manga')
        if page:
            if page.manga.pk != manga.pk:
                raise serializers.ValidationError(
                    'Manga page cannot refer to this manga')
        return attrs


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content"]


class VoteSerializer(serializers.Serializer):
    vote = serializers.IntegerField()

    def validate_vote(self, value):
        if value not in [-1, 1]:
            raise serializers.ValidationError(
                "Invalid vote value. Must be -1 or 1.")
        return value
    

class RatingSerializer(serializers.ModelSerializer):
    star = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        model = Rating
        fields = ['id', 'star', 'manga']
        extra_kwargs = {
            'manga': {'write_only': True}
        }

    def validate_manga(self, value):
        try:
            Manga.objects.get(pk=value.pk)
        except Manga.DoesNotExist:
            raise serializers.ValidationError("Manga not found.")
        return value
