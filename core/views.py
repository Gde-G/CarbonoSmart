from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from cities_light.models import Country
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from datetime import datetime, timedelta

from blog.models import Article
from .forms import CompanyForm


def index(request: HttpRequest):
    last_3_articles = Article.objects.filter(
        publish_date__lte=timezone.now()).order_by('-publish_date')[:3]

    context = {
        'last_3_articles': last_3_articles,
        'cons_msg': ''
    }
    return render(request, 'core/index.html', context=context)


def about_us(request: HttpRequest):
    return render(request, 'core/about-us.html')


def pirv_policy(request: HttpRequest):
    return render(request, 'core/private-policy.html')


def term_use(request: HttpRequest):
    return render(request, 'core/terms-use.html')


def contact(request: HttpRequest):
    return render(request, 'core/contact.html')


def companies_contact(request: HttpRequest):
    countries = Country.objects.all()
    form = CompanyForm()
    if request.method == 'POST':
        phone = '+' + Country.objects.get(id=request.POST.get(
            'country')).phone + request.POST.get('contact_phone')
        request.POST = request.POST.copy()
        request.POST['contact_phone'] = phone

        form = CompanyForm(request.POST)
        if form.is_valid():
            try:
                org_consult = form.save()

                if len(org_consult.content) == 0:
                    messages.error(
                        request, 'Es imposible enviar una consulta vacia.')
                    return redirect(request.META['HTTP_REFERER'])
                mail_subject = f"Consulta desde la pagina echa por la organizacion {org_consult.name}"
                if org_consult.website != None:
                    org_web = org_consult.website
                else:
                    org_web = 'No Ingresado'
                context = {
                    'org_consult': org_consult,
                    'org_web': org_web,
                    'datetime': timezone.now(),
                }
                temp = get_template('core/email_org_consultation.html')

                content = temp.render(context)

                corr = EmailMultiAlternatives(
                    subject=mail_subject,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[settings.EMAIL_HOST_USER],
                    reply_to=[org_consult.contact_email]
                )

                corr.attach_alternative(content, 'text/html')
                corr.send(fail_silently=False)
                messages.info(
                    request, 'Consulta enviada con exito. En la brevedad recibira la respuesta a su email!')
            except:
                messages.error(
                    request, 'Algo salio mal al enviar la consulta, intente nuevamente mas tarde!')
            return redirect(request.META['HTTP_REFERER'])
        else:
            for errors, fields in form.errors.as_data().items():
                messages.error(
                    request, f'Error: {errors}. {fields}!')

    context = {
        'countries': countries,
        'form': form,
        'page': 'sign-in'
    }
    return render(request, 'core/companies-form.html', context=context)


def code_form_country(request: HttpRequest):
    country_id = request.GET.get('country_id')
    country = get_object_or_404(Country, id=country_id)

    return JsonResponse({"code_phone": '+' + str(country.phone)})


@login_required
@require_http_methods(['POST'])
def fast_contact(request: HttpRequest):
    try:
        user = request.user
        content = request.POST.get('consultation')
        if len(content) == 0:
            return render(request, 'partials/fast-consult.html',
                          context={'cons_msg': '<p class="htmx-text-error"><i class="fa-regular fa-circle-xmark"></i> Es imposible enviar una consulta vacia'})

        mail_subject = f"Consulta desde la pagina echa por {user.username}"

        context = {
            'user': user,
            'content': content,
            'datetime': timezone.now(),
            'domain': get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http',
        }
        temp = get_template('core/email_consultation.html')

        content = temp.render(context)

        corr = EmailMultiAlternatives(
            subject=mail_subject,
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_HOST_USER],
            reply_to=[user.email]
        )

        corr.attach_alternative(content, 'text/html')
        corr.send(fail_silently=False)
        return render(request, 'partials/fast-consult.html',
                      context={'cons_msg': f'<p class="htmx-text-success"> Consulta enviada con exito. En la brevedad recibira la respuesta a su email(el cual esta vinculado a su cuenta)!</p>'})
    except:
        return render(request, 'partials/fast-consult.html',
                      context={'cons_msg': f'<p class="htmx-text-error"><i class="fa-regular fa-circle-xmark"></i> Algo salio mal al enviar la consulta, intente nuevamente mas tarde!</p>'})


def our_service(request: HttpRequest):
    return render(request, 'core/our-service.html')


def marketplace(request: HttpRequest):
    return render(request, 'core/marketplace.html')


def set_consent(request: HttpRequest):
    response = render(request, 'partials/cookie-consent.html',
                      context={'consent': True})
    expiration = datetime.now() + timedelta(days=365)
    response.set_cookie(key="consent", value="true", expires=expiration)
    return response
