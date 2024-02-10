from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_index, name='blog'),

    path('category/<str:slug>', views.get_category, name='category'),
    path('categories/', views.get_categories, name='categories'),
    path('add-category/', views.create_category, name="add-category"),
    path('edit-category/<str:slug>', views.edit_category, name="edit-category"),
    path('del-category/<str:slug>', views.delete_category, name="del-category"),

    path('add-article/', views.create_article, name='add-article'),
    path('article/<str:slug>', views.get_article, name='article'),
    path('edit-article/<str:slug>', views.edit_article, name='edit-article'),
    path('del-article/<str:slug>', views.delete_article, name="del-article"),

    path('article/<str:slug>/like', views.like_article, name='like-article'),
    path('article/<str:slug>/dislike',
         views.dislike_article, name='dislike-article'),

    path('article/<str:slug>/add-comment',
         views.create_comment, name='add-comment'),

    path('article/<str:slug>/comment/<str:id>/add-reply',
         views.create_reply_comment, name='add-reply-comment'),
    path('article/<str:slug>/del-comment/<str:id>',
         views.del_comment, name='del-comment'),
]

htmx_urlpatterns = [
    path('category-offcanvas/', views.display_category_of_canvas,
         name='category-offcanvas'),
    path('validate-category-name/',
         views.validate_category_name, name='validate-cate-name')
]

urlpatterns += htmx_urlpatterns
