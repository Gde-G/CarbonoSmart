# Generated by Django 4.2.2 on 2023-07-02 18:00

import ckeditor_uploader.fields
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('subtitle', models.CharField(max_length=500)),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True)),
                ('slug', models.SlugField(blank=True, max_length=160, null=True, unique=True)),
                ('prin_img', models.ImageField(upload_to='images/blog/article_prin')),
                ('views', models.PositiveIntegerField(default=0)),
                ('shared_count', models.PositiveIntegerField(default=0)),
                ('publish_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(max_length=300)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('prin_img', models.ImageField(upload_to='images/blog/categories')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=750)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_parent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_read', models.BooleanField(default=False)),
                ('content', models.TextField()),
                ('content_id', models.PositiveIntegerField()),
                ('article_slug', models.CharField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
