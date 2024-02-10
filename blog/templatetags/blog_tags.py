from django import template
from django.utils import timezone
from django.template.defaultfilters import stringfilter
from user.models import MyUser
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def future_date(date):
    return date > timezone.now()


@register.filter
@stringfilter
def upto(value: str, delimiter=None):
    return value.split(delimiter)[0]


upto.is_safe = True


@register.filter
def substract_one(value):
    return int(value) - 1


@register.filter(name='mention', is_safe=True)
@stringfilter
def mention(value):
    res = ""
    my_list = value.split()
    for i in my_list:
        if i[0] == '@':
            try:
                username = i[1:]
                user = MyUser.objects.get(username=username)
                if user:
                    i = f"<span class='comment-mention'>{i}</span>"

            except:
                pass

        res = res + i + ' '

    return mark_safe(res)


@register.filter
def search_term(content, term):

    return not (term in content)
