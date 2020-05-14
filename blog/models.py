from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from read_statistics.models import ReadNumExpandMethod,ReadDetail
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.fields import GenericRelation



class BlogType(models.Model):
    type_name = models.CharField(max_length=30)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.type_name

class Blog(models.Model,ReadNumExpandMethod):
    title = models.CharField(max_length=100)
    blog_type = models.ForeignKey(BlogType,on_delete=models.CASCADE)
    content = RichTextUploadingField()
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    read_detail = GenericRelation(ReadDetail)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def get_url(self):
        return reverse('blog_detail',kwargs={'blog_pk':self.pk})

    def get_email(self):
        return self.author.email

    def get_title(self):
        return '博客'

    def __str__(self):
        return '<Blog: %s>' %self.title

    class Meta:
        ordering = ['-create_time']
