from django.conf import settings
from django.db import models
from django.utils import timezone

class AwarenessPost(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='awareness_posts')
    title = models.CharField(max_length=150)
    content = models.TextField()
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='awareness/', blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def increment_views(self):
        self.views_count += 1
        self.save()

    def __str__(self):
        return self.title