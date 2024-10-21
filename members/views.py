from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
  # Import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.context_processors import csrf
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm 
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from .forms import DoctorForm,FeedbackForm, LoginForm, DeathCertificateForm, PostmortemForm, EmbalmerForm,DisposalForm,PathologistForm,RegistrationForm
from .models import Deceased,Feedback, Doctor,Disposal,Notification,DeathCertificate,DeathRegistration,Embalmer,Postmortem
from django.contrib import admin,messages # For displaying success or error messages
from calendar import month_name  # For getting the names of months
from django.db.models import Count  # For counting in Django queries
from django.db.models.functions import ExtractMonth  # For extracting month from dates
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json,logging


# view for error handling 
logger = logging.getLogger(__name__)

def my_view(request):
    try:
        # Your view logic here
        # Example: perform some database operations, etc.
        pass  # Replace with actual logic
    except Exception as e:
        logger.error('An error occurred: %s', str(e))
        # Handle the error (return an error response, etc.)
        return HttpResponse('An error occurred. Please try again later.', status=500)



def new_death_registered():
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'death_updates',  # Name of the group
        {
            'type': 'send_update',
            'message': 'A new death has been registered'
        }
    )

# View for blog_feedback Form
def blog_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            # Send email to admin
            send_mail(
                subject=f"New Feedback from {form.cleaned_data['user_name']}",
                message=form.cleaned_data['message'],
                from_email=form.cleaned_data['user_email'],
                recipient_list=[settings.ADMIN_EMAIL],  # Add admin email in settings.py
                fail_silently=False,
            )
            return redirect('feedback_success')  # Redirect to a success page after submission
    else:
        form = FeedbackForm()

    return render(request, 'blog_feedback.html', {'form': form})

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'user_email', 'sent_at']

admin.site.register(Feedback, FeedbackAdmin)

# View for Doctor Form
def doctor_form(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            # Create the User instance
            user = User.objects.create_user(
                username=form.cleaned_data['username'],  # Use the username field from the form
                password=form.cleaned_data['password'],  # Ensure password is in the form
                email=form.cleaned_data['email'],  # Email from form
            )

            # Save the doctor instance from the form
            doctor = form.save(commit=False)  # Use commit=False to modify before saving

            # Set the User instance to the doctor
            doctor.user = user
            doctor.save()  # Save the doctor instance

            # Automatically log in the user after registration
            login(request, user)

            # Redirect to the doctor's dashboard after successful registration
            return redirect('login')  # Ensure this URL is defined in your urls.py
    else:
        form = DoctorForm()

    return render(request, 'members/templates/members/doctor_form.html', {'form': form})  # Adjust the template path as necessary
  
# View for registering Form
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        
        if form.is_valid():
            # Create the user object but don't save to the database yet
            user = form.save(commit=False)
            
            # Set the password (hashes it properly)
            user.set_password(form.cleaned_data['password'])
            
            # Save the user object to the database
            user.save()
            
            # Show a success message
            messages.success(request, 'Registration successful.')
            
            # Automatically log in the user
            login(request, user)
            
            # Get the specialization field from the form
            specialization = form.cleaned_data['specialization']
            
            # Redirect the user based on their specialization
            if specialization == 'doctor':
                return redirect('doctor_registration_form')  # Redirect to Doctor Registration Form
            elif specialization == 'admin':
                return redirect('admin_dashboard')  # Redirect to Admin Dashboard
            elif specialization == 'pathologist':
                return redirect('pathologist_registration_form')  # Redirect to Pathologist registration form
            else:
                return redirect('home')  # Default redirect if specialization is not recognized
        else:
            # Add errors to the form if invalid
            form.add_error(None, "Please correct the errors below.")
    else:
        # Instantiate a blank registration form if it's a GET request
        form = RegistrationForm()

    # Render the registration page with the form
    return render(request, 'members/register.html', {'form': form})
 
 
 # View for pathologist Form


def pathologist_registration_view(request):
    context = {}

    if request.method == 'POST':
        form = PathologistForm(request.POST)
        if form.is_valid():
            # Create the pathologist object but don't save it yet
            pathologist = form.save(commit=False)
            
            # Hash the password before saving
            pathologist.password = make_password(form.cleaned_data['password'])
            
            # Save the pathologist object
            pathologist.save()

            # Redirect to login page after registration
            return redirect('login')  # Adjust this to your login URL name
    else:
        form = PathologistForm()

    context['form'] = form

    return render(request, 'members/pathologist_registration_form.html', context)
 
 # View for pathologist_dashboard Form
@login_required
def pathologist_dashboard(request):
    return render(request, 'pathologist_dashboard.html')

 # View for doctor_registration_view Form
def doctor_registration_view(request):
    context = {}
    context.update(csrf(request))
    print(request.META.get('CSRF_COOKIE')) 

    if request.method == 'POST':
        form = DoctorForm(request.POST)
        
        if form.is_valid():
            form.save()  # Save doctor's information
            return redirect('doctor_list')  # Redirect to Doctor Dashboard after successful registration
    else:
        form = DoctorForm()
        
        context['form'] = form
    
        
    return render(request, 'members/doctor_registration.html', {'form': form})
 
    
# View for Login Form
def login_view(request):
    print(settings.TEMPLATES[0]['DIRS'])  # Print the directories being searched
    
    # Check if the request method is POST
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            specialization = form.cleaned_data['specialization']
            
            # Check if input is email or username and authenticate accordingly
            if '@' in username_or_email:
                user = authenticate(request, email=username_or_email, password=password)
            else:
                user = authenticate(request, username=username_or_email, password=password)

            # If user is authenticated successfully
            if user is not None:
                login(request, user)  # Log the user in
                # Redirect based on specialization
                if specialization == 'admin':
                    return redirect('admin_dashboard')
                elif specialization == 'doctor':
                    return redirect('doctor_dashboard')
                elif specialization == 'pathologist':
                    return redirect('pathologist_dashboard')
            else:
                # Invalid credentials handling
                form.add_error(None, "Invalid credentials")
    else:
        # For GET requests, create a blank form
            return HttpResponseNotFound('Invalid username or password.')  # Return a 404 error page

    # Pass the form to the template
    return render(request, 'members/login.html', {'form': form})


 
 #view for deceased table

def deceased_table_view(request):
    deceased_list = Deceased.objects.all()
    return render(request, 'deceased_table.html', {'deceased_list': deceased_list})

  #view for deceased table

def doctor_table_view(request):
    pass

 # View for doctor_dashboard Form

def doctor_dashboard(request):
    return render(request, 'doctor_dashboard.html')
 

# View for Death Certificate Form
def death_certificate_form(request):
    form = DeathCertificateForm()
    return render(request, 'members/death_certificate_form.html', {'form': form})

@login_required
def print_death_certificate_view(request, certificate_id):
    certificate = get_object_or_404(DeathCertificate, id=certificate_id)
    
    return render(request, 'print_death_certificate.html', {'certificate': certificate})

# View for Disposal Form
def Disposal_Form(request):
    if request.method == 'POST':
        form = DisposalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect to a success page or another view
    else:
        form = DisposalForm()
    return render(request, 'members/templates/members/disposal.html', {'form': form})

# View for Postmortem Form
def postmortem_form(request):
    form = PostmortemForm()
    return render(request, 'members/postmortem_form.html', {'form': form})

@login_required
def print_postmortem_view(request, postmortem_id):
    postmortem = get_object_or_404(Postmortem, id=postmortem_id)
    
    return render(request, 'print_postmortem.html', {'postmortem': postmortem})

# View for Embalmer Form
def embalmer_form(request):
    form = EmbalmerForm()
    return render(request, 'members/embalmer_form.html', {'form': form})
 
 # View for NextOfKinForm Form

@login_required
def print_embalmer_view(request, embalmer_id):
    embalmer = get_object_or_404(Embalmer, id=embalmer_id)
    
    return render(request, 'print_embalmer.html', {'embalmer': embalmer})

def NextOfKinForm(request):
    form = NextOfKinForm()
    return render(request, 'members/NextOfKinForm.html', {'form': form})

# View for edit_profile_view
@login_required
def edit_profile_view(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to a profile view or dashboard
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'form': form})

# View for DASHBOARD
@login_required  # Ensures only logged-in users can access the dashboard
def Admin_dashboard_view(request):
    user_name = request.user.username
    
    # Fetch unread notifications
    notifications = Notification.objects.filter(is_read=False).order_by('-timestamp')

    # Handle form submission for registering new users or other POST actions (example)
    if request.method == 'POST':
        # Create a new notification after a new user registration (example)
        Notification.objects.create(message="New user registered: Dr. John Doe", is_read=False)

    # Calculate totals for burial, cremation, deceased, and doctors
    burial_count = Disposal.objects.filter(type='burial').count()
    cremation_count = Disposal.objects.filter(type='cremation').count()
    deceased_count = Deceased.objects.count()
    doctor_count = Doctor.objects.count()

    deceased_records = Deceased.objects.all() 
    # Prepare bar chart data (dummy data, replace with real data)
    bar_chart_data = {
        'labels': ['2019', '2020', '2021', '2022', '2023'],
        'data': [100, 150, 200, 250, 300]
    }

    # Get monthly death counts for line chart
    monthly_deaths = Deceased.objects.annotate(month=ExtractMonth('date_of_death')).values('month').annotate(count=Count('id')).order_by('month')
    
    # Prepare line chart data
    line_chart_data = {
        'labels': [month_name[death['month']] for death in monthly_deaths],  # Month names
        'data': [death['count'] for death in monthly_deaths]  # Death counts per month
    }

    # Context to pass to the template
    context = {
        'notifications': notifications,
        'user_name': user_name,
        'deceased_count': deceased_count,
        'doctor_count': doctor_count,
        'burial_count': burial_count,
        'cremation_count': cremation_count,
        'line_chart_data': json.dumps(line_chart_data),  # Pass data as JSON
        'bar_chart_data': json.dumps(bar_chart_data),    # Pass data as JSON
    }

    return render(request, 'Admin_dashboard.html', context)

def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect('Admin_dashboard.html',{'deceased_records': Deceased})  # Adjust to your actual dashboard URL


def register_death(request):
    if request.method == 'POST':
        # Handle the form submission for registering a death
        deceased = Deceased.objects.create(
            name=request.POST.get('name'),
            date_of_death=request.POST.get('date_of_death'),
            # Other fields...
        )
        
        # Generate the death certificate
        certificate_number = get_random_string(10)
        DeathCertificate.objects.create(
            deceased=deceased,
            certificate_number=certificate_number,
            issued_by=Doctor,  # Link to the doctor issuing it
        )

        return redirect('some_dashboard')
    else:
        return render(request, 'register_death.html')


def death_certificate_view(request):
    certificates = DeathCertificate.objects.all()
    return render(request, 'death_certificate_view.html', {'certificates': certificates})
