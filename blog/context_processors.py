from django.http import HttpRequest
from .models import Category, Notification


def get_categories_list(request: HttpRequest):

    return {
        "category_each": [
            {"name": category.name, "slug": category.slug}
            for category in Category.objects.all()
        ]
    }


def get_notifications_amount(request: HttpRequest):
    if request.user.is_authenticated:
        notifications_amount = Notification.objects.filter(
            recipient=request.user, is_read=False).count()

        return {'noti_amount': notifications_amount}
    else:
        return {'noti_amount': 0}
