from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime


class CustomUser(AbstractUser):

    avatar = models.ImageField(upload_to="user/avatars/", default="user/avatar/default.jpg")
    backround_image = models.ImageField(upload_to="user/backgrounds/", blank=True)


class MangaUserList(models.Model):
    LIST_TYPE = (
        ("reading", "Читаю"),
        ("planned", "В планах"),
        ("dropped", "Брошено"),
        ("readed", "Прочитано"),
        ("favorite", "Любимые"),
    )

    manga = models.ForeignKey("manga.Manga", on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='manga_list')
    list_type = models.CharField(choices=LIST_TYPE, max_length=20)
    created_at = models.DateTimeField(default=datetime.datetime.now())
    comment = models.TextField(max_length=90, blank=True, null=True)
