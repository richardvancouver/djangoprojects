from django.db import models 
from django.contrib.flatpages.models import FlatPage
from django.contrib import admin

# Create your models here.


class SearchKeyword(models.Model):
    keyword = models.CharField(max_length=50)
    page = models.ForeignKey(FlatPage)

    #class Author:pass

    def __unicode__(self):
        return self.keyword

#admin.site.register(SearchKeyword.Author)
