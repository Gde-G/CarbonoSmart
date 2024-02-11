from django.urls import path, include
from .import views
urlpatterns = [
    path('get-regions', views.get_regions, name='get-regions'),
    path('get-cities', views.get_cities, name='get-cities'),


    path('profile/', views.profile, name='account_profile'),
    path('edit-profile/', views.update_profile, name='edit-profile'),
    path('del-profile/', views.delete_user, name='del-profile'),
    path('profile-notification/', views.notifications_profile,
         name='profile-notifications'),
    path('profile-likes/', views.likes_profile, name='likes-profile'),
    path('password-set/',
         views.password_setup, name='password_set'),

    path('accounts/password/reset/done/', views.account_reset_password_done,
         name='account_reset_password_done'),

    path('accounts/signup/', views.sign_up, name='account_signup'),
    path('accounts/inactive/', views.inactive_account, name='account_inactive'),
    path('accounts/confirm-email/', views.account_email_verification_sent,
         name='account_email_verification_sent'),
    path('accounts/confirm-email/<uidb64>/<token> ',
         views.activate, name='account_confirm_email'),
    path('accounts/password/reset/key/done/', views.account_reset_password_from_key_done,
         name='account_reset_password_from_key_done'),

    path('accounts/social/signup/', views.socialaccount_signup,
         name='socialaccount_signup')
]

htmx_urlpatterns = [
    path('login-dropdown/', views.login_dropdown, name='login-dropdown'),
]
urlpatterns += htmx_urlpatterns
