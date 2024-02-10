from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField


from user.models import MyUser
import re
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300)
    slug = models.SlugField(blank=True, null=True)
    prin_img = models.ImageField(upload_to='images/blog/categories')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=500)
    keywords = models.CharField(max_length=100)
    content = RichTextUploadingField(blank=True, null=False)
    slug = models.SlugField(max_length=160, blank=True, null=True, unique=True)
    prin_img = models.ImageField(upload_to='images/blog/article_prin')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    shared_count = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(
        MyUser, related_name='likes_articles', blank=True)
    dislikes = models.ManyToManyField(
        MyUser, related_name='dislikes_articles', blank=True)

    publish_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.TextField(max_length=750)
    created_at = models.DateTimeField(auto_now_add=True)

    parent_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    user_mentions = models.ManyToManyField(
        MyUser, related_name='mentioned_in_comments')

    is_parent = models.BooleanField(default=False)

    ordered = ['-created_at']

    def get_replies(self):
        return Comment.objects.filter(parent_comment=self)

    def find_mentions(self):
        mention_matches = re.findall(r'@(\w+)', self.content)

        return mention_matches

    def __str__(self):
        return self.content


class Notification(models.Model):
    sender = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        MyUser, on_delete=models.CASCADE,  related_name='sent_notifications')
    is_read = models.BooleanField(default=False)
    content = models.TextField()
    content_id = models.PositiveIntegerField()
    article_slug = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)

    def notification_reply(self, sender, reply):
        if len(reply) > 80:
            reply = reply[:79]

        self.content = f"{sender.username.capitalize()} contesto tu comentario: {reply}..."

    def notification_meniton(self, sender, comment):
        if len(comment) > 80:
            comment = comment[:79]

        self.content = f"{sender.username.capitalize()} te menciono en un comentario: {comment}..."

    def __str__(self):
        return self.content
