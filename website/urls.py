from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.landing, name='landing'),
    # urls.py
    path('home', views.home, name='home'),  # Home page
    path('blog/', views.blog, name='blog'),  # Blog page
    path('about-us/', views.about, name='about'),  # About Us page
    path('contact-us/', views.contact_us, name='contact_us'),  # Contact Us page
]
