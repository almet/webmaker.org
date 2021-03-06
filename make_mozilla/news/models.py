import lxml.html

from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    summary = models.TextField(blank=True, null=True)
    page = models.CharField(max_length=50)
    checksum = models.CharField(max_length=32, unique=True)
    updated = models.DateTimeField()
    autor = models.CharField(max_length=255)
    featured = models.BooleanField(default=False)

    def get_feature_image(self):
        html = lxml.html.fromstring(self.summary)
        imgs = html.cssselect('img')
        if len(imgs) != 0:
            return lxml.html.tostring(imgs[0])

    def get_summary(self):
        return self.summary

    def __unicode__(self):
        return '%s' % (
            self.title,
        )
