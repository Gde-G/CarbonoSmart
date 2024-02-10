from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from blog.views import notifications_navbar

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('notifications-nav/', notifications_navbar, name='notifications'),
    path('', include('core.urls')),
    path('', include('user.urls')),
    path('', include('user.urls')),
    path('accounts/', include('allauth.urls')),
    path('blog/', include('blog.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
