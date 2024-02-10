from django import forms
from .models import *


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'prin_img']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'content',
                  'prin_img', 'category', 'publish_date']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class ReplyCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['parent_comment', 'content']
