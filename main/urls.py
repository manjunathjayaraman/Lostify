from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('google-login/', views.google_login, name='google_login'),

    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp_view, name='resend_otp'),

    path('report-lost/', views.report_lost, name='report_lost'),
    path('report-found/', views.report_found, name='report_found'),
    path('find-items/', views.find_items, name='find_items'),
    path('my-status/', views.my_status, name='my_status'),

    path('mark-lost-item-found/<int:lost_id>/<int:found_id>/', views.mark_lost_item_found, name='mark_lost_item_found'),
    path('claim-found-item/<int:found_id>/', views.claim_found_item, name='claim_found_item'),

    path('help/', views.help_view, name='help'),
    path('contact-us/', views.contact_us_view, name='contact_us'),
    path('settings/', views.settings_view, name='settings'),
    path('my-profile/', views.profile_view, name='my_profile'),
]