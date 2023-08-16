from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Blogs(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    published = models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    # t_post
    class Meta:
        db_table = "t_blogs"
        # unique index on title & author
        constraints = [
            models.UniqueConstraint(fields=["title", "author"], name="unique_post")
        ]
