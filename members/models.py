from django.db import models
from datetime import datetime
from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncYear
from django.utils.crypto import get_random_string
from django.core.validators import MinLengthValidator, RegexValidator


# UserProfile table
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

# FEEDBACK table
class Feedback(models.Model):
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user_name} at {self.sent_at}"

# Deceased table
class Deceased(models.Model):
    id = models.AutoField(primary_key=True)
    DEATH_PLACES = [('home', 'Home'), ('hospital', 'Hospital'), ('other', 'Other')]
    home_address = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=100, validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Only letters are allowed in the name')])
    age = models.IntegerField()
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    description = models.TextField(max_length=100)
    date_of_birth = models.DateField()
    date_of_death = models.DateField()
    cause_of_death = models.TextField()
    funeral_home_name = models.CharField(max_length=255)
    place_of_death = models.CharField(max_length=255, choices=DEATH_PLACES)

    def __str__(self):
        return f'{self.full_name} - {self.date_of_death}'
# Next of kin table
class NextOfKin(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=100, validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Only letters are allowed in the name')])
    nrc = models.CharField(max_length=12, validators=[RegexValidator(r'^[0-9/]{9,10}$', 'NRC must be 9 or 10 characters and include numbers and /')])
    contact = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,}$', 'Contact number must be at least 10 digits and only contain numbers')])
    email = models.EmailField(null=True, blank=True)
    relationship_to_deceased = models.CharField(max_length=100)
    additional_notes = models.TextField(null=True, blank=True)
    
    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, related_name='next_of_kin')

    def __str__(self):
        return f'{self.full_name} ({self.relationship_to_deceased}) - Next of Kin for {self.deceased.full_name}'

# Doctor's table
class Doctor(models.Model):
    license_id = models.CharField(max_length=100, unique=True, primary_key=True)
    username = models.CharField(max_length=100, null=True, validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Only letters are allowed in the name')])
    contact_info = models.CharField(max_length=15,validators=[RegexValidator(r'^\d{10,}$', 'Contact number must be at least 10 digits and only contain numbers')])
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    hospital_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, default='Lusaka')
    NRC = models.CharField(max_length=12, unique=True)
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return f'{self.username} - {self.license_id}'

# Disposal table
class Disposal(models.Model):
    DISPOSAL_TYPES = [
        ('buried', 'Buried'),
        ('cremated', 'Cremated'),
        ('other', 'Other'),
    ]

    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, related_name='disposals')
    approved_by = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, related_name='approved_disposals')
    type_of_disposal = models.CharField(max_length=10, choices=DISPOSAL_TYPES)
    site_of_disposal = models.CharField(max_length=255)
    funeral_home_name = models.CharField(max_length=255)
    date_of_disposal = models.DateField()
    additional_notes = models.TextField(null=True, blank=True)
    
    @staticmethod
    def calculate_total_disposals(disposal_type):
        return Disposal.objects.filter(type_of_disposal=disposal_type).count()

    def __str__(self):
        return f'Deceased {self.deceased.id} was {self.get_type_of_disposal_display()} on {self.date_of_disposal}'

# Pathologist table
class Pathologist(models.Model):
    name = models.CharField(max_length=100, validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Only letters are allowed in the name')])
    license_id = models.CharField(max_length=50)  # Add this field
    contact_info = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,}$', 'Contact number must be at least 10 digits and only contain numbers')])
    NRC = models.CharField(max_length=12, validators=[RegexValidator(r'^[0-9/]{9,10}$', 'NRC must be 9 or 10 characters and include numbers and /')], unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=128)  # Add this field
    hospital_name = models.CharField(max_length=255)
    branch = models.CharField(max_length=100, default='Lusaka')
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name

# Death certificate model
class DeathCertificate(models.Model):
    certificate_number = models.CharField(max_length=20, unique=True, blank=True)
    registration = models.OneToOneField('DeathRegistration', on_delete=models.CASCADE, related_name='certificate')
    issued_by = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='issued_certificates')
    issue_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = self.generate_certificate_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_certificate_number():
        year = datetime.now().year
        random_part = get_random_string(6)
        return f"DC-{year}-{random_part}"

    def __str__(self):
        return f"Certificate {self.certificate_number} for {self.registration.deceased.full_name}"
# Death registration table
class DeathRegistration(models.Model):
    id = models.AutoField(primary_key=True)  # Explicit primary key
    deceased_name = models.CharField(max_length=255)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    registration_date = models.DateField(auto_now_add=True)  # Automatically set the registration date
    remarks = models.TextField(null=True, blank=True)
    disposal_permit = models.ForeignKey(Disposal, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = (('deceased_name', 'doctor'),)

    def save(self, *args, **kwargs):
        # Create the deceased record if it doesn't exist
        if not self.deceased:
            # You need to extract these values from your registration form (you might want to pass them as kwargs)
            deceased_data = {
                'full_name': self.full_name,  # You need to have this in the form or the model
                'age': self.age,              # Same as above
                'gender': self.gender,        # Same as above
                'description': self.description,  # Same as above
                'date_of_birth': self.date_of_birth,  # Same as above
                'date_of_death': self.date_of_death,  # Same as above
                'cause_of_death': self.cause_of_death,  # Same as above
                'funeral_home_name': self.funeral_home_name,  # Same as above
                'place_of_death': self.place_of_death  # Same as above
            }
            self.deceased = Deceased.objects.create(**deceased_data)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Registration of {self.deceased.deceased_name} by Dr. {self.doctor.name}'

# Get the total deaths per month (for the current year)
def get_monthly_deaths():
    return (
        DeathRegistration.objects.filter(date_registered__year=datetime.now().year)
        .annotate(month=TruncMonth('date_registered'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

# Get the total deaths per year (for the past years)
def get_yearly_deaths():
    return (
        DeathRegistration.objects
        .annotate(year=TruncYear('date_registered'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )


# Postmortem table
class Postmortem(models.Model):
    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE)
    pathologist = models.ForeignKey(Pathologist, on_delete=models.CASCADE)
    report = models.TextField()
    date_conducted = models.DateField()

    def __str__(self):
        return f'Postmortem for {self.deceased.full_name}'

# Embalmer table
class Embalmer(models.Model):
    license_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=100, validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Only letters are allowed in the name')])
    contact_info = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,}$', 'Contact number must be at least 10 digits and only contain numbers')])
    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE)
    embalming_details = models.TextField()
    date_of_embalming = models.DateField()
    nrc = models.CharField(max_length=12, validators=[RegexValidator(r'^[0-9/]{9,10}$', 'NRC must be 9 or 10 characters and include numbers and /')], unique=True)

    def __str__(self):
        return f'Embalmer: {self.name} for {self.deceased.full_name}'

# NOTIFICATIONS
class Notification(models.Model):
    message = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message