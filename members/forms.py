from django.shortcuts import render, redirect
from django import forms
from .models import UserProfile
from django.contrib.auth.models import User
from .models import Doctor,NextOfKin,Deceased, Embalmer, Postmortem, Pathologist
from .models import DeathRegistration,Feedback, DeathCertificate, Disposal
from django.core.exceptions import ValidationError



class BootstrapMixin:
    """
    Mixin to apply Bootstrap classes to form fields.
    """
    def apply_bootstrap(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_photo']

# FORM FOR FEEDBACK
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['user_name', 'user_email', 'message']

class DisposalForm(forms.ModelForm):
    class Meta:
        model = Disposal
        fields = '__all__'

# FORM FOR NEXT OF KIN
class NextOfKinForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = NextOfKin
        fields = '__all__'
    
    def apply_bootstrap(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


# FORM FOR DECEASED
class DeceasedForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Deceased
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap() 
             
# FORM FOR DOCTOR REGISTRATION
class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor  # Specify the model
        fields = ['username', 'license_id', 'contact_info', 'NRC', 'email', 'password', 'hospital_name', 'branch', 'gender']
        
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'license_id': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control'}),
            'NRC': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'branch': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

def doctor_registration(request):
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Replace with your success URL
    else:
        form = DoctorForm()
    
    return render(request, 'your_template.html', {'form': form})


# FORM FOR PATHOLOGIST
class PathologistForm(forms.ModelForm):  # Change to ModelForm
    class Meta:
        model = Pathologist  # Specify the model
        fields = [
            'name',
            'license_id',
            'contact_info',
            'NRC',
            'email',
            'password',
            'hospital_name',
            'branch',
            'gender',
        ]

    # You can keep this method if you want to customize the form further
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can apply any additional bootstrap styles or configurations here
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'  # Apply Bootstrap styles


# DEATH REGISTRATION FORM
class DeathRegistrationForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = DeathRegistration
        fields = '__all__'
           
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()# Call the method to apply Bootstrap styles

# FORM FOR DEATH CERTIFICATE
class DeathCertificateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = DeathCertificate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

# FORM FOR DEATH POSTMORTEM
class PostmortemForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Postmortem
        fields = [
            'deceased',  # Linking to the deceased
            'pathologist',  # Pathologist who conducted the postmortem
            'report',
            'date_conducted',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class EmbalmerForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Embalmer
        fields = [
            'license_id',  # Primary key of the embalmer
            'name',
            'contact_info',
            'deceased',  # Linking to the deceased
            'embalming_details',
            'date_of_embalming',
            'nrc',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
 # FORM FOR REGISTRATION

# FORM FOR REGISTRATION BUTTON
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        min_length=5,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    specialization = forms.ChoiceField(choices=[
        ('doctor', 'Doctor'),
        ('pathologist', 'Pathologist'),
    ], widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'specialization']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        # Validate that passwords match
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Validate minimum password length
        if len(password) < 5:
            raise forms.ValidationError("Password must be at least 5 characters long.")

        # Validate unique username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose a different one.")

        # Validate unique email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use. Please choose a different one.")

        return cleaned_data  # Return cleaned data to ensure it can be used later
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to the database yet
            user.set_password(form.cleaned_data['password'])  # Set the password correctly
            user.save()  # Now save the user
        return redirect('success')  # Redirect to a success page or dashboard
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

# FORM FOR LOGIN
class LoginForm(forms.Form):
    username_or_email = forms.CharField(label="Username or Email", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    SPECIALIZATIONS = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('pathologist', 'Pathologist')
    ]
    specialization = forms.ChoiceField(label="Specialization", choices=SPECIALIZATIONS)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 5:
            raise forms.ValidationError("Password must be at least 5 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

 