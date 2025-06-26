from django.db import models

class UserDownload(models.Model):
    title = models.CharField(max_length=250)
    videoSlug = models.SlugField(max_length=250)
    date = models.TextField()
    userIp = models.TextField(default=False)