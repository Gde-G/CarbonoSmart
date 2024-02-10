from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about-us/', views.about_us, name="about-us"),
    path('privacy-policy/', views.pirv_policy, name='priv-policy'),
    path('term-use/', views.term_use, name='term-use'),
    path('contact/', views.contact, name='contact'),
    path('companies-contact/', views.companies_contact, name='companies-contact'),
    path('get-phone-code/', views.code_form_country, name='phone-code'),

    path('services/', views.our_service, name='our-services'),
    path('marketplace/', views.marketplace, name='marketplace')
]

htmx_urlpatterns = [
    path('fast-consultation/', views.fast_contact, name='fast-consultation'),
    path('consent/', views.set_consent, name='consent')
]

urlpatterns += htmx_urlpatterns
