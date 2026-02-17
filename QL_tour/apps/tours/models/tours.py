from django.db import models
from .categories import Category
from .country import Country
from django.contrib.gis.db import models

class Status(models.TextChoices):
    DRAFT = 'DRAFT', 'Nháp'
    ACTIVE = 'ACTIVE', 'Kích hoạt'
    HIDDEN = 'HIDDEN', 'Ẩn'

def user_avatar_path(instance, filename):
    return f"avatars/user_{instance.id}/{filename}"

class Tour(models.Model):
    title = models.CharField()
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.DateTimeField()
    max_people = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', default='avatars/default.jpg', blank=True)
    status = models.CharField(choices=Status.choices, default=Status.ACTIVE)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
