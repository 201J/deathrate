from django.urls import path
from . import views
from .views import Admin_dashboard, mark_as_read,edit_profile_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    path('edit-profile/', edit_profile_view, name='edit_profile'),
    path('register/', views.register_view, name='register'),
    path('doctor-registration/', views.doctor_registration_view, name='doctor_registration_form'),
    path('deceased_table/', views.deceased_table_view, name='deceased_table'),
    path('doctor_table/', views.doctor_table_view, name='doctor_table'),
    path('doctor', views.doctor_form, name='doctor_form'),
    path('NextOfKin', views.NextOfKinForm, name='NextOfKin'),
    path('Disposal', views.Disposal_Form, name='Disposal'),  # Fixed Disposal_Form view name
    path('login/', views.login_view, name='login'),
    path('death-certificate/form/', views.death_certificate_form, name='death_certificate_form'),
    path('postmortem/form/', views.postmortem_form, name='postmortem_form'),
    path('embalmer/form/', views.embalmer_form, name='embalmer_form'),
    path('pathologist_registration/', views.pathologist_registration_view, name='pathologist_registration_form'),
    path('Admin_dashboard/', views.Admin_dashboard_view, name='Admin_dashboard_view'),
    path('register/', views.doctor_registration_view, name='doctor_registration_view'),
    path('doctor/dashboard/', views.doctor_dashboard, name='Doctor_dashboard.html'),
    path('pathologist/dashboard/', views.pathologist_dashboard, name='pathologist_dashboard'),
    path('admin/notification/mark_as_read/<int:notification_id>/', mark_as_read, name='mark_as_read'),
     path('print/death-certificate/<int:certificate_id>/', print_death_certificate_view, name='print_death_certificate'),
    path('print/postmortem/<int:postmortem_id>/', print_postmortem_view, name='print_postmortem'),
    path('print/embalmer/<int:embalmer_id>/', print_embalmer_view, name='print_embalmer'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home.html'), name='logout'),  # Logout URL

]

