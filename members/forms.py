from django import forms
from .models import Doctor,NextOfKin,Deceased, Embalmer, Postmortem, Pathologist
from .models import DeathRegistration, DeathCertificate, Disposal


class BootstrapMixin:
    """
    Mixin to apply Bootstrap classes to form fields.
    """
    def apply_bootstrap(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })

class DisposalForm(forms.ModelForm):
    class Meta:
        model = Disposal
        fields = [
            'deceased',  # Just the field name, not the field definition
            'type_of_disposal',
            'site_of_disposal',
            'funeral_home_name',
            'date_of_disposal',
            'additional_notes',
            'approved_by',
        ]

# FORM FOR NEXT OF KIN
class NextOfKinForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = NextOfKin
        fields = [
            'full_name',
            'nrc',
            'contact',
            'email',
            'relationship_to_deceased',
            'additional_notes',
            'deceased',  # Linking to the deceased
        ]
    def apply_bootstrap(self):
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


# FORM FOR DECEASED
class DeceasedForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Deceased
        fields = [
            'full_name',
            'age',
            'gender',
            'description',
            'date_of_birth',
            'date_of_death',
            'cause_of_death',
            'funeral_home_name',
            'place_of_death',
            'home_address',
            # 'disposal',  # Linking to the disposal method
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap() 
             
# FORM FOR DOCTOR
class DoctorForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = Doctor
        fields = [
            'license_id',
            'name',  # This field should exist in the Doctor model
            'contact_info',
            'email',
            'password',  # Handle password securely
            'specialization',  # This field should exist in the Doctor model
            'hospital_name',
            'branch',
            'NRC',
            'gender',  # This field should exist in the Doctor model
        ]

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)
        # Apply Bootstrap styling to all form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
 # PATHOLOGIST  FORM     
class PathologistForm(forms.ModelForm):
    class Meta:
        model = Pathologist
        fields = ['name','NRC','email', 'contact_info', 'gender','hospital_name','branch']

# DEATH REGISTRATION FORM
class DeathRegistrationForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = DeathRegistration
        fields = [
            'deceased',  # Linking to the deceased
            'doctor',  # Doctor registering the death
            'registration_date',
            'remarks',
            'disposal_permit',  # Linking to the disposal permit
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()# Call the method to apply Bootstrap styles

# FORM FOR DEATH CERTIFICATE
class DeathCertificateForm(forms.ModelForm, BootstrapMixin):
    class Meta:
        model = DeathCertificate
        fields = [
            'deceased',  # Linking to the deceased
            'doctor',  # Doctor issuing the certificate    
            'date_issued',
            'certificate_number',
        ]

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
 
 # FORM FOR LOGIN
class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100)
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    # Add specialization field
    SPECIALIZATIONS = [('doctor', 'Doctor'), ('pathologist', 'Pathologist')]
    specialization = forms.ChoiceField( label="Specialization",choices=SPECIALIZATIONS )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        # Check if password and confirm password match
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")


 