from django.shortcuts import render

# Landing page view
def landing(request):
    return render(request, "website/landing.html")

# home page view
def home(request):
    return render(request, 'website/home.html')
#blog page view
def blog(request):
    return render(request, 'website/blog.html')
#about us view
def about(request):
    return render(request, 'website/about.html')
#contact us view
def contact_us(request):
    return render(request, 'website/contact_us.html')
