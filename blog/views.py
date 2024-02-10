from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseNotFound, JsonResponse, HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import get_object_or_404
from django.utils.timesince import timesince
from django.urls import reverse

from user.models import MyUser
from .models import *
from .forms import *

import re


def articles_paginator(obj_list, pages):
    paginator = Paginator(object_list=obj_list, per_page=3)

    try:
        articles = paginator.get_page(pages)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)

    return articles


def blog_index(request: HttpRequest):
    query = request.GET.get('q-search')

    sort_by = request.GET.get('sort')

    if sort_by == 'ancient':
        order = 'publish_date'
    elif sort_by == 'views':
        order = '-views'
    elif sort_by == 'liked':
        order = 'likes'
    else:
        order = '-publish_date'

    if query is None:
        if request.user.is_staff:
            articles = Article.objects.all().order_by(order)

        else:
            articles = Article.objects.filter(
                publish_date__lte=timezone.now()).order_by(order)
    else:
        if request.user.is_staff:
            articles = Article.objects.filter(
                Q(title__icontains=query) | Q(
                    subtitle__icontains=query) | Q(
                    category__name__icontains=query)).order_by(order)

        else:
            articles = Article.objects.filter(
                Q(publish_date__lte=timezone.now()) & (
                    Q(title__icontains=query) | Q(
                        subtitle__icontains=query) | Q(
                        category__name__icontains=query))).order_by(order)

    articles = articles_paginator(articles, request.GET.get('p'))

    categories = Category.objects.all()
    get_copy = request.GET.copy()
    parameters_url = get_copy.pop('p', True) and get_copy.urlencode()

    context = {
        'articles': articles,
        'categories': categories,
        'q_search': query,
        'sort_by': sort_by,
        'parameters': parameters_url
    }
    return render(request, 'blog/blog.html', context=context)


@staff_member_required
@require_http_methods(['GET'])
def display_category_of_canvas(request: HttpRequest):
    return render(request, 'partials/category-offcanvas.html')


@staff_member_required
@require_http_methods(['GET'])
def validate_category_name(request: HttpRequest):
    name = request.GET.get('name')
    if Category.objects.filter(name__exact=name).exists():
        return HttpResponse(
            f'''
            <div class="mb-3" hx-target="this" hx-swap="outerHTML""
              hx-target="this" hx-swap="outerHTML">
        
              <label for="id_name" class="form-label">Nombre</label>
              <input type="text" class="form-control border-2 border-danger"
                name="name" id="id_name" maxlength="100" 
                value="{name}" autocomplete="off" required
                hx-get="{reverse('validate-cate-name')}"  hx-trigger="input delay:1s">
              <p class='htmx-text-error'><i class="fa-regular fa-circle-xmark"></i> Ya existe una categoria con este nombre</p>  
            </div>
            
            '''
        )
    else:
        return HttpResponse(
            f'''
            <div class="mb-3" hx-target="this" hx-swap="outerHTML""
              hx-target="this" hx-swap="outerHTML">
        
             <label for="id_name" class="form-label">Nombre</label>
             <input type="text" class="form-control border-2 border-success"
                name="name" id="id_name" maxlength="100" 
                value="{name}" autocomplete="off" required
                hx-get="{reverse('validate-cate-name')}" hx-trigger="input delay:1s">
            </div>
            '''
        )


@staff_member_required
@require_http_methods(['POST'])
def create_category(request: HttpRequest):
    form = CategoryForm(request.POST, request.FILES)

    if form.is_valid():
        category = form.save()
        return redirect('categories')
    else:
        for field, error in form.errors.as_data().items():
            messages.error(request, f'Error:{error[0].messages[0]}')

    return redirect(request.META['HTTP_REFERER'])


def get_category(request: HttpRequest, slug):
    query = request.GET.get('q-search')
    category = Category.objects.get(slug=slug)
    categories = Category.objects.all()
    sort_by = request.GET.get('sort')
    if sort_by == 'ancient':
        order = 'publish_date'
    elif sort_by == 'views':
        order = '-views'
    elif sort_by == 'liked':
        order = 'likes'
    else:
        order = '-publish_date'
    if query is None:
        if request.user.is_staff:
            articles = Article.objects.filter(
                Q(category__id__exact=category.id)).order_by(order)
        else:
            articles = Article.objects.filter(
                Q(category__id__exact=category.id) & Q(publish_date__lte=timezone.now())).order_by(order)
    else:
        if request.user.is_staff:
            articles = Article.objects.filter(Q(category__id__exact=category.id) & (Q(
                title__icontains=query) | Q(
                subtitle__icontains=query))).order_by(order)
        else:
            articles = Article.objects.filter(
                (Q(category__id__exact=category.id) & Q(
                    publish_date__lte=timezone.now())) & (Q(
                        title__icontains=query) | Q(
                        subtitle__icontains=query))).order_by(order)

    articles = articles_paginator(articles, request.GET.get('p'))

    get_copy = request.GET.copy()
    parameters_url = get_copy.pop('p', True) and get_copy.urlencode()

    context = {
        'articles': articles,
        'category': category,
        'categories': categories,
        'q_search': query,
        'sort_by': sort_by,
        'parameters': parameters_url
    }

    return render(request, 'blog/blog.html', context=context)


def get_categories(request: HttpRequest):
    categories = Category.objects.all()

    context = {
        'categories': categories
    }
    return render(request, 'blog/categories.html', context=context)


@staff_member_required
def edit_category(request: HttpRequest, slug):
    category = Category.objects.get(slug=slug)
    form = CategoryForm(instance=category)

    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)

        if form.is_valid():
            category = form.save()
            return redirect('categories')
        else:
            for field, error in form.errors.as_data().items():
                messages.error(request, f'{field}:,{error}')

    return redirect(request.META['HTTP_REFERER'])


@staff_member_required
def delete_category(request: HttpRequest, slug):
    category = Category.objects.get(slug=slug)

    if request.method == "POST":
        try:
            name = category.name
            category.delete()
            messages.success(
                request, f'Categoria:{name}. Fue Eliminada de manera exitosa!')
            return redirect('categories')
        except:
            messages.error(
                request, 'Error, no fue posible eliminar el categoria.')
            return redirect('categories')
    context = {
        'category': category
    }
    return render(request, 'blog/categories.html', context=context)


@staff_member_required
def create_article(request: HttpRequest):
    categories = Category.objects.all()
    form = ArticleForm()

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()
            return redirect('article', article.slug)
        else:
            for field, error in form.errors.as_data().items():
                messages.error(request, f'{field}, {error}')

    context = {
        'categories': categories,
        'form': form
    }

    return render(request, 'blog/create-article.html', context=context)


def get_article(request: HttpRequest, slug):

    article = Article.objects.get(slug=slug)
    comments = Comment.objects.filter(
        article=article, parent_comment=None).order_by('-created_at')

    comments_replies = Comment.objects.filter(
        article=article, parent_comment__isnull=False).order_by('-created_at')

    article.views += 1
    article.save()
    liked = True if article.likes.filter(
        id=request.user.id).exists() else False

    disliked = True if article.dislikes.filter(
        id=request.user.id).exists() else False

    context = {
        'article': article,
        'likes_amount': article.likes.count(),
        'liked': liked,
        'disliked': disliked,
        'comments': comments,
        'comments_replies': comments_replies,
    }
    return render(request, 'blog/article.html', context=context)


@staff_member_required
def edit_article(request: HttpRequest, slug):
    article = Article.objects.get(slug=slug)
    categories = Category.objects.all()
    form = ArticleForm(instance=article)

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            article.save()

            return redirect('article', slug)
        else:
            for field, error in form.errors.as_data().items():
                messages.error(request, f'{field}, {error}')

    context = {
        'article': article,
        'categories': categories,
        'form': form
    }

    return render(request, 'blog/edit-article.html', context=context)


@staff_member_required
def delete_article(request: HttpRequest, slug):
    article = Article.objects.get(slug=slug)

    if request.method == "POST":
        try:
            title = article.title
            article.delete()
            messages.success(
                request, f'Articulo:{title}. Fue Eliminado de manera exitosa!')
            return redirect('blog')
        except:
            messages.error(
                request, 'Error, no fue posible eliminar el articulo.')
            return redirect('blog')
    context = {
        'article': article
    }
    return render(request, 'blog/article.html', context=context)


@csrf_exempt
def like_article(request: HttpRequest, slug):
    try:
        article = get_object_or_404(Article, slug=slug)
        if article.likes.filter(id=request.user.id).exists():
            article.likes.remove(request.user)
        else:
            if article.dislikes.filter(id=request.user.id).exists():
                article.dislikes.remove(request.user)

            article.likes.add(request.user)
        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({"status": 'error'})


@csrf_exempt
def dislike_article(request: HttpRequest, slug):
    try:
        article = get_object_or_404(Article, slug=slug)
        if article.dislikes.filter(id=request.user.id).exists():
            article.dislikes.remove(request.user)
        else:
            if article.likes.filter(id=request.user.id).exists():
                article.likes.remove(request.user)

            article.dislikes.add(request.user)
        return JsonResponse({'status': 'success'})
    except:
        return JsonResponse({"status": 'error'})


def create_comment(request: HttpRequest, slug):
    article = Article.objects.get(slug=slug)
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user
            comment.save()
            mentions = comment.find_mentions()
            if len(mentions) > 0:
                for each in mentions:
                    try:
                        user_mentionate = MyUser.objects.get(username=each)

                        comment.user_mentions.add(user_mentionate)
                        if comment.user != user_mentionate:
                            notificaiton = Notification(
                                sender=comment.user,
                                recipient=user_mentionate,
                                article_slug=slug,
                                content_id=comment.id
                            )
                            notificaiton.notification_meniton(
                                comment.user, comment.content)
                            notificaiton.save()

                    except:
                        continue

            return JsonResponse({'status': 'success',
                                 'username': comment.user.username,
                                 'user_img': '/' + str(comment.user.profile_img),
                                 'id': comment.id})
        else:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


def create_reply_comment(request: HttpRequest, slug, id):
    article = Article.objects.get(slug=slug)
    form = ReplyCommentForm()

    if request.method == 'POST':
        form = ReplyCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)

            parent_comment = Comment.objects.get(
                id=id)

            comment.parent_comment = parent_comment
            comment.article = article
            comment.user = request.user

            parent_comment.is_parent = True
            parent_comment.save()
            comment.save()
            if comment.user != parent_comment.user:
                notificaiton = Notification(
                    sender=comment.user,
                    recipient=parent_comment.user,
                    article_slug=slug,
                    content_id=parent_comment.id
                )
                notificaiton.notification_reply(comment.user, comment.content)
                notificaiton.save()

            mentions = comment.find_mentions()

            if len(mentions) > 0:
                for each in mentions:
                    try:
                        user_mentionate = MyUser.objects.get(username=each)
                        comment.user_mentions.add(user_mentionate)
                        if parent_comment.user != user_mentionate:
                            notificaiton2 = Notification(
                                sender=comment.user,
                                recipient=user_mentionate,
                                article_slug=slug,
                                content_id=parent_comment.id
                            )
                            notificaiton2.notification_meniton(
                                comment.user, comment.content)
                            notificaiton2.save()
                    except:
                        print('error')

            return JsonResponse({'status': 'success',
                                'username': comment.user.username,
                                 'user_img': '/' + str(comment.user.profile_img),
                                 'id': comment.id})

        else:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})


def del_comment(request: HttpRequest, slug, id):
    comment = Comment.objects.get(id=id)

    try:
        if request.user == comment.user or request.user.is_staff == True:
            if comment.parent_comment == None:
                comment.delete()
            else:
                parent_comment = Comment.objects.get(
                    id=comment.parent_comment.id)
                comment.delete()

                if len(parent_comment.get_replies()) <= 0:
                    parent_comment.is_parent = False
                    parent_comment.save()

            return redirect('article', slug)
        else:
            return HttpResponseNotFound("Access Denied!")
    except:
        messages.error(
            request, f'Error al eliminar el comentario. Intente mas tarde!')
    return redirect('article', slug)


def notifications_navbar(request: HttpRequest):
    if request.user.is_authenticated:
        user = request.user
        notifications = Notification.objects.filter(
            recipient=user, is_read=False).order_by('-created_at')
        len(notifications)

        notifications_data = [{'status': 'success'}] + [{
            'sender': notification.sender.username,
            'sender_img': '/' + str(notification.sender.profile_img),
            'content': notification.content,
            'date': timesince(notification.created_at).split(',')[0],
            'article_slug': notification.article_slug,
            'content_id': notification.content_id,
        }for notification in notifications]

        notifications.update(is_read=True)

        return JsonResponse(notifications_data, safe=False)

    else:
        return JsonResponse([{'status': 'Access Denied!'}], safe=False)
