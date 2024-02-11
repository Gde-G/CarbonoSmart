from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils.timesince import timesince
from allauth.account.models import EmailAddress
from cities_light.models import Country, Region, City

from blog.models import Notification, Article
from .models import MyUser
from .tokens import account_activation_token
from .decorators import user_not_authenticated
from .forms import *
from .authbackends import MyUserBackend


@login_required(login_url='account_login')
def profile(request: HttpRequest):
    return render(request, 'account/profile.html')


def activate_with_email(request, user, to_email):
    try:
        mail_subject = "Bienvenido/a a Carbono Smart - Confirmación de Registro"

        context = {
            'user': user.username,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http',
        }

        temp = get_template(
            'account/email/email_confirmation_message.html')

        content = temp.render(context)

        corr = EmailMultiAlternatives(
            subject=mail_subject,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )

        corr.attach_alternative(content, 'text/html')
        corr.send(fail_silently=False)

        messages.success(
            request, f'Hola {user}, ve a tu bandeja de entrada de correo electrónico {to_email} y haz clic en el enlace de activación recibido para confirmar y completar el registro. Nota: Verifica tu carpeta de correo no deseado (spam).')
    except:
        messages.error(
            request, f'Problema al enviar el correo electrónico de confirmación a {to_email}, verifica si lo has escrito correctamente.')


@user_not_authenticated
def sign_up(request: HttpRequest):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()
            EmailAddress.objects.create(
                email=user.email, primary=True, user_id=user.pk)
            activate_with_email(request, user, form.cleaned_data.get('email'))

            return redirect('home')

        else:
            for field, error in form.errors.as_data().items():
                messages.error(request, f"ERROR: {field}, {error[0].messages}")

    context = {
        'page': 'sign-in',
        'form_sign': form
    }

    return render(request, 'account/signup.html', context=context)


def socialaccount_signup(request: HttpRequest):

    if request.method == 'POST':
        form = MyUserAllauthSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.save()
            EmailAddress.objects.create(
                email=user.email, primary=True, user_id=user.pk)
            activate_with_email(request, user)
            messages.success(request, f'Le enviamos un email para que active su email. Recuerde revisar su casilla de SPAM.')
            return redirect('home')  
        else:
            for field, error in form.errors.as_data().items():
                messages.error(request, f"ERROR: {field}, {error[0].messages}")

    else:
        form = MyUserAllauthSignUpForm()
    return render(request, 'socialaccount/signup.html', {'form': form})
    


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(pk=uid)
        email_address: EmailAddress = EmailAddress.objects.get(
            email=user.email)
    except (TypeError, ValueError, OverflowError, MyUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        email_address.verified = True
        email_address.save()
        user.save()

        messages.success(
            request, 'Gracias por comfirmar tu registro.')
        login(request, user, backend='user.authbackends.MyUserBackend')
        return redirect('home')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('home')


@user_not_authenticated
def login_dropdown(request: HttpRequest):
    form = MyUserLoginForm()
    if request.method == 'POST':
        form = MyUserLoginForm(request=request, data=request.POST)

        if form.is_valid():
            remember = form.cleaned_data['remember']

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )

            if user is not None:
                if user.is_active:
                    login(request, user)

                    if not remember:
                        request.session.set_expiry(0)

                else:
                    activate_with_email(request, user, user.email)
                    messages.error(
                        request, f"Su cuenta esta inactiva, para activarla ingrese al email con el cual se creo la cuenta y activela con el email que le mandamos al momento de crearse la cuenta!")
                return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, f"Ingrese bien los datos!")
        else:

            for field, error in form.errors.as_data().items():
                if field == "captcha" and error[0] == 'This field is required.':
                    messages.error(
                        request, "ERROR, debe pasar el captcha.")
                    continue
                elif error[0] == 'This account is inactive.':
                    messages.error(
                        request, "La cuenta con la que intenta iniciar seccion esta inactiva.")
                else:
                    messages.error(
                        request, f"Error: {error[0].messages[0]}")

    context = {'formLogin': form}
    return render(request, 'core/index.html', context=context)


def inactive_account(request: HttpRequest):

    messages.info(request,
                  "Esta cuenta esta inactiva, en su momento le enviamos un email al correo ingresado para que pueda activar su cuenta!")
    return redirect(request.META['HTTP_REFERER'])


def account_email_verification_sent(request: HttpRequest):
    messages.info(request, 'Le hemos enviado un correo electrónico para su verificación. Siga el enlace proporcionado para finalizar el proceso de registro. Si no ve el correo electrónico de verificación en su bandeja de entrada principal, revise su carpeta de correo no deseado. Comuníquese con nosotros si no recibe el correo electrónico de verificación dentro de unos minutos.')
    return redirect('home')


@login_required(login_url='account_login')
def password_setup(request):

    user = MyUser.objects.get(pk=request.user.pk)
    form = MyUserSocialAccountSetForm(user)

    if user is not None:
        if SocialAccount.objects.filter(user=user).exists():
            if request.method == 'POST':
                form = MyUserSocialAccountSetForm(user, request.POST)
                if form.is_valid():
                    new_username = request.POST.get('username')
                    if MyUser.objects.filter(username=new_username).exists() and user.username != new_username:
                        messages.error(
                            request, f'Ya esta en uso el nombre de usuario {new_username}, elija otro!')
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        user.username = new_username
                    form.save()
                    user.save()
                    login(request, user, backend='user.authbackends.MyUserBackend')
                    messages.success(
                        request, f"¡Felicidades {user.username}, tu cuenta se ha creado correctamente! Inicia sesión para acceder.")
                else:
                    for error in list(form.errors.values()):
                        messages.error(request, error)

                return redirect('home')

        else:
            return redirect(request.META['HTTP_REFERER'])

    context = {
        'user': user,
        'form': form
    }

    return render(request, 'user/password-setup-social.html', context=context)


def account_reset_password_done(request: HttpRequest):
    messages.info(request, 'Te hemos enviado un correo electrónico. Si no lo has recibido por favor revisa tu carpeta de spam. En caso contrario contacta con nosotros si no lo recibes en unos minutos.')
    return redirect('home')


def account_reset_password_from_key_done(request: HttpRequest):
    messages.success(request, 'Su contraseña a sido cambiada exitosamente!')
    return redirect('home')


def get_regions(request: HttpRequest):
    country_id = request.GET.get('country_id')
    country = get_object_or_404(Country, id=country_id)
    print(country.phone)
    regions_of_country = Region.objects.filter(country=country)

    regions_data = {region.pk: region.name for region in regions_of_country}
    regions_data['country_phone_code'] = country.phone
    return JsonResponse(regions_data, safe=False)


def get_cities(request: HttpRequest):
    region_id = request.GET.get('region_id')

    region = get_object_or_404(Region, id=region_id)
    cities_of_region = City.objects.filter(region=region)

    cities_data = {
        city.pk: city.name for city in cities_of_region}

    return JsonResponse(cities_data)


@login_required(login_url='account_login')
def update_profile(request: HttpRequest):
    user = MyUser.objects.get(id=request.user.id)
    countries = Country.objects.all()
    form = MyUserUpdateForm(instance=user)

    if user.profile_img:
        img_have = 'True'

    else:
        img_have = 'False'

    if request.method == 'POST':
        form = MyUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            messages.success(
                request, f'{user.username.capitalize()} su perfil a a actualizado!')

            return redirect('account_profile')
        else:
            for field, error in form.errors.as_data().items():
                if error[0] == 'Custom user with this Email already exists.':
                    messages.error(
                        request, f'Error: ese Email ya esta en uso por otro usuario!')
                else:
                    messages.error(
                        request, f'Error:, {error[0].messages[0]} ')

    context = {
        'form': form,
        'user': user,
        'img_have': img_have,
        'countries': countries,
    }

    return render(request, 'user/update-profile.html', context=context)


@login_required(login_url='account_login')
def notifications_profile(request: HttpRequest):
    if request.user.is_authenticated:
        user = request.user
        notifications = Notification.objects.filter(
            recipient=user).order_by('-created_at')

        notifications_data = [{'status': 'success'}] + [{
            'sender': notification.sender.username,
            'sender_img': '/' + str(notification.sender.profile_img),
            'content': notification.content,
            'date': timesince(notification.created_at).split(',')[0],
            'article_slug': notification.article_slug,
            'content_id': notification.content_id,
        }for notification in notifications]

        return JsonResponse(notifications_data, safe=False)

    else:
        return JsonResponse([{'status': 'Access Denied!'}], safe=False)


@login_required(login_url='account_login')
def likes_profile(request: HttpRequest):
    if request.user.is_authenticated:
        user = request.user
        likes_articles = Article.objects.filter(
            likes=user).order_by('-created_at')

        likes_data = [{'status': 'success'}] + [{
            'title': article.title,
            'prin_img': '/' + str(article.prin_img),
            'article_category': article.category.name,
            'date': timesince(article.created_at).split(',')[0],
            'article_slug': article.slug,
        }for article in likes_articles]

        return JsonResponse(likes_data, safe=False)

    else:
        return JsonResponse([{'status': 'Access Denied!'}], safe=False)

@login_required(login_url='account_login')
def delete_user(request: HttpRequest):
    user = MyUser.objects.get(id=request.user.id) 
    if request.method == 'POST':
        user.delete()
        return redirect('home')
    else:
        messages.error(request, 'Algo ha salido mal, intent mas tarde!')
        return  redirect('edit-profile')