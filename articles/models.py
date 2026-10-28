from django.db import models


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField()

    def __str__(self) -> str:
        return self.title
