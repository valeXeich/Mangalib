from django.urls import path
from rest_framework import routers

from .views import (MangaViewSet,
                    GenresListAPIView, 
                    MangaTypeAPIView, 
                    CommentViewSet, TagListAPIView, ChapterViewSet, RatingViewSet)


router = routers.DefaultRouter()
router.register(r"manga", MangaViewSet)
router.register(r"comments", CommentViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'ratings', RatingViewSet)

urlpatterns = [
    path("rating/user_rating/<int:manga_pk>/", RatingViewSet.as_view({"get": "user_rating"})),
    path("genres/", GenresListAPIView.as_view()),
    path("tags/", TagListAPIView.as_view()),
    path("types/", MangaTypeAPIView.as_view())
]

urlpatterns += router.urls