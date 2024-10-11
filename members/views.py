from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import DoctorForm, LoginForm, DeathCertificateForm, PostmortemForm, EmbalmerForm,DisposalForm,PathologistForm
from .models import Deceased, Doctor,Disposal


# View for Doctor Form
def doctor_form(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            # Save the doctor instance from the form
            doctor = form.save(commit=False)  # Use commit=False to modify before saving

            # Create the User instance
            user = User.objects.create_user(
                username=doctor.name,  # Assuming 'name' field is used for username
                password=form.cleaned_data.get('password'),  # Adjust to your form
                email=doctor.email,  # Ensure your form captures an email field
            )

            # Optionally, set the user as the doctor instance's user
            doctor.user = user  # Assuming you have a ForeignKey relationship
            doctor.save()  # Save the doctor instance

            # Automatically log in the user after registration
            login(request, user)

            # Redirect to the dashboard after successful registration
            return redirect('dashboard_view')
    else:
        form = DoctorForm()

    # Fetch all Disposal instances regardless of POST or GET
    disposals = Disposal.objects.all()
    return render(request, 'members/doctor_form.html', {
        'form': form,
        'disposals': disposals  # Pass the disposals data to the template
    })
    # View for Login Form
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            specialization = form.cleaned_data.get('specialization')

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

                # Redirect based on specialization
                if specialization == 'doctor':
                    return redirect('doctor_form')  # Redirect to DoctorForm view
                elif specialization == 'pathologist':
                    return redirect('pathologist_form.html')  # Redirect to PathologistForm view
            else:
                form.add_error(None, "Invalid login credentials.")
    else:
        form = LoginForm()

    return render(request, 'members/login.html', {'form': form})
# View for doctors Form
def doctor_form_view(request):
    # Handle the doctor's form submission logic here
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctor_dashboard')
    else:
        form = DoctorForm()

    return render(request, 'doctor_form.html', {'form': form})
# View for pathologist Form
def pathologist_form(request):
    if request.method == 'POST':
        form = PathologistForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctor_list')
    else:
        form = PathologistForm()

    return render(request, 'pathologist_form.html', {'form': form})

# View for Death Certificate Form
def death_certificate_form(request):
    form = DeathCertificateForm()
    return render(request, 'members/death_certificate_form.html', {'form': form})

# View for Disposal Form
def Disposal_Form(request):
    if request.method == 'POST':
        form = DisposalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Redirect to a success page or another view
    else:
        form = DisposalForm()
    return render(request, 'template_name.html', {'form': form})

# View for Postmortem Form
def postmortem_form(request):
    form = PostmortemForm()
    return render(request, 'members/postmortem_form.html', {'form': form})

# View for Embalmer Form
def embalmer_form(request):
    form = EmbalmerForm()
    return render(request, 'members/embalmer_form.html', {'form': form})
 
 # View for NextOfKinForm Form
def NextOfKinForm(request):
    form = NextOfKinForm()
    return render(request, 'members/NextOfKinForm.html', {'form': form})

# View for DASHBOARD
@login_required  # Ensures only logged-in users can access the dashboard
def dashboard_view(request):
    # Example data for charts
    line_chart_data = [50, 60, 70, 85, 75, 90, 100]  # Death count per month
    bar_chart_data = [20, 30, 25, 40, 35]  # Death count per year (last 5 years)

    # Aggregating statistics from the models
    deceased_count = Deceased.objects.count()
    doctor_count = Doctor.objects.count()
    burial_count = Disposal.objects.filter(type_of_disposal='buried').count()
    cremation_count = Disposal.objects.filter(type_of_disposal='cremated').count()

    # Prepare the context data to pass to the template
    context = {
        'user_name': request.user.username,  # Retrieves the logged-in user's name
        'line_chart_data': line_chart_data,
        'bar_chart_data': bar_chart_data,
        'deceased_count': deceased_count,
        'doctor_count': doctor_count,
        'burial_count': burial_count,
        'cremation_count': cremation_count,
    }

    # Render the dashboard template with context data
    return render(request, 'dashboard.html', context)