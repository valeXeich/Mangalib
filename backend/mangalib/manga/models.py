from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from .utils import background_image_upload_path, poster_image_upload_path, page_image_upload_path

User = get_user_model()


class AbstractModel(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
    

class Genre(AbstractModel):
    pass


class Author(AbstractModel):
    pass


class Publisher(AbstractModel):
    pass


class Painter(AbstractModel):
    pass


class Tag(AbstractModel):
    pass


class Manga(models.Model):
    MANGA_TYPE = (
        ("manga", "Manga"),
        ("manhwa", "Manhwa"),
        ("manhua", "Manhua"),
    )

    MANGA_STATUS = (
        ("ongoing", "Ongoing"),
        ("planned", "Planned"),
        ("released", "Released"),
        ("suspended", "Suspended"),
    )

    AGE_RATING = (
        ("absent", "Absent"),
        ("16+", "16+"),
        ("18+", "18+")
    )

    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=MANGA_TYPE)
    age_rating = models.CharField(max_length=20, choices=AGE_RATING)
    image = models.ImageField(upload_to=poster_image_upload_path)
    related_manga = models.ManyToManyField("self", blank=True)
    release_year = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=MANGA_STATUS, default="planned")
    backround_image = models.ImageField(upload_to=background_image_upload_path, blank=True)
    genres = models.ManyToManyField(Genre)
    tag = models.ManyToManyField(Tag, blank=True)
    view_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='manga')
    publisher = models.ManyToManyField(Publisher, related_name='manga')
    painter = models.ForeignKey(Painter, on_delete=models.CASCADE, related_name='manga')
    slug = models.SlugField(unique=True, null=True)

    def __str__(self):
        return self.title
    
    def get_total_chapters(self):
        total = 0
        for volume in self.volumes.all():
            total += volume.chapters.count()
        return total
    
    def get_avg_rating(self):
        avg_rating = self.ratings.aggregate(Avg('star')).get('star__avg')
        return avg_rating or 0
    
    def get_ratings(self):
        ratings = self.ratings.all()
        rating_counts = {i: 0 for i in range(1, 11)}
        total_ratings = ratings.count()
        for rating in ratings:
            rating_counts[rating.star] += 1
        rating_data = []
        for star, total_rated in rating_counts.items():
            percent = (total_rated / total_ratings) * 100 if total_ratings > 0 else 0
            rating_data.append({"star": star, "total": total_rated, "percent": percent})
        return {"total_rated": total_ratings, "ratings": rating_data}
    
    def get_user_list(self):
        user_list = [
            {"status": "read", "total": self.readers.count()},
            {"status": "planned", "total": self.plans.count()},
            {"status": "dropped", "total": self.drops.count()},
            {"status": "readed", "total": self.read.count()},
            {"status": "favorite", "total": self.favorites.count()},
        ]
        total_users = sum(item["total"] for item in user_list)
        for item in user_list:
            item["percent"] = (item["total"] / total_users) * 100 if total_users > 0 else 0
        return {"total_users": total_users, "user_list": user_list}


class Volume(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="volumes")
    volume_number = models.IntegerField()

    def __str__(self):
        return f"Manga: {self.manga.title} Volume: {self.volume_number}"


class Chapter(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name="chapters")
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="chapters", default=None, blank=True, null=True)
    chapter_number = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=100, null=True)
    slug = models.SlugField(null=True)

    def __str__(self):
        return f"Manga: {self.volume.manga.title}: Chapter: {self.title}"


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name="pages")
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="pages", default=None, blank=True, null=True)
    page_number = models.IntegerField()
    image = models.ImageField(upload_to=page_image_upload_path)

    def __str__(self):
        return f"Manga: {self.chapter.volume.manga.title} Page number: {self.page_number}"


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, null=True, blank=True)
    manga_page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    is_page_comment = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_parent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Author {self.author} Manga: {self.manga.title}'


class RatingComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="ratings")
    vote = models.IntegerField(choices=[(1, 'Like'), (-1, 'Dislike')])


class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ratings"
    )
    star = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        default=0
    )
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name="ratings")

    def __str__(self):
        return f"User {self.user.username} Manga: {self.manga.title} Rating: {self.star}"
    
