from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('doctor', views.doctor_form, name='doctor_form'),
    path('nextofkin', views.NextOfKinForm, name='nextofkin'),
    path('disposal', views.Disposal_Form, name='disposal'),  # Fixed Disposal_Form view name
    path('login/', views.login_view, name='login_form'),
    path('death-certificate/form/', views.death_certificate_form, name='death_certificate_form'),
    path('postmortem/form/', views.postmortem_form, name='postmortem_form'),
    path('embalmer/form/', views.embalmer_form, name='embalmer_form'),
    path('pathologist/form/', views.pathologist_form, name='pathologist_form'),
    path('dashboard/', views.dashboard_view, name='dashboard.html'),

    # Add the logout view
    path('logout/', auth_views.LogoutView.as_view(next_page='home.html'), name='logout'),  # Logout URL
]

