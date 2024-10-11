from django.db import models

# Deceased table
class Deceased(models.Model):
    id = models.AutoField(primary_key=True)  # Primary Key (Django automatically adds this if not specified)
    DEATH_PLACES = [('home', 'Home'), ('hospital', 'Hospital'), ('other', 'Other')]
    home_address = models.CharField(max_length=255, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    age = models.TextField(max_length=4)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    description = models.TextField(max_length=100)
    date_of_birth = models.DateField()
    date_of_death = models.DateField()
    cause_of_death = models.TextField()
    funeral_home_name = models.CharField(max_length=255)  # Name of the funeral home handling the disposal
    place_of_death = models.CharField(max_length=255, choices=DEATH_PLACES)

    # Foreign key to Disposal table
    # disposal = models.ForeignKey('Disposal', on_delete=models.SET_NULL, null=True)
    # disposals = models.ManyToManyField(
    #     Disposal,
    #     related_name='deceased_disposals',  # Change this if necessary
    #     blank=True,
    # )

    def __str__(self):
        return f'{self.full_name} - {self.date_of_death}'

    # Next of kin table
class NextOfKin(models.Model):
    id = models.AutoField(primary_key=True)  # Primary Key (Django automatically adds this if not specified)
    full_name = models.CharField(max_length=100)
    nrc = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    relationship_to_deceased = models.CharField(max_length=100)
    additional_notes = models.TextField(null=True, blank=True)
    
    # Foreign key to the Deceased table
    deceased = models.ForeignKey('Deceased', on_delete=models.CASCADE, related_name='next_of_kin')

    def __str__(self):
        return f'{self.full_name} ({self.relationship_to_deceased}) - Next of Kin for {self.deceased.full_name}'


# Doctor's table (with license_id as primary key)
class Doctor(models.Model):
    license_id = models.CharField(max_length=100, unique=True, primary_key=True)  # Primary Key
    name = models.CharField(max_length=100)  # Make sure the name field exists here
    contact_info = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Ideally, this should be handled securely
    SPECIALIZATIONS = [('doctor', 'Doctor'), ('pathologist', 'Pathologist')]
    specialization = models.CharField(max_length=100, choices=SPECIALIZATIONS, default='doctor')  # Ensure specialization exists
    hospital_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, default='Lusaka')
    NRC = models.CharField(max_length=100, unique=True)
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)  # Ensure gender exists

    def __str__(self):
        return f'{self.name} - {self.specialization}'


    # DISPOSAL table
class Disposal(models.Model):
    DISPOSAL_TYPES = [
        ('buried', 'Buried'),
        ('cremated', 'Cremated'),
        ('other', 'Other'),
    ]
    
    deceased = models.ForeignKey(
        'Deceased',
        on_delete=models.CASCADE,
        related_name='disposals'  # Ensure this is unique and does not clash
    )
    type_of_disposal = models.CharField(max_length=50, choices=DISPOSAL_TYPES)
    site_of_disposal = models.CharField(max_length=255)
    funeral_home_name = models.CharField(max_length=255)
    date_of_disposal = models.DateField()
    additional_notes = models.TextField(null=True, blank=True)
    
    approved_by = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_disposals'
    )

    def __str__(self):
        return f'Deceased ID: {self.deceased.id}, Name: {self.deceased.full_name}, was {self.get_type_of_disposal_display()} on {self.date_of_disposal}'

# Pathologist table (with hospital name and branch)
class Pathologist(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255)
    hospital_name = models.CharField(max_length=255)
    branch = models.CharField(max_length=100, default='Lusaka')
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'),]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)  # Ensure gender exists
    NRC = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=255, unique=True)

    def __str__(self):
        return self.name


# Death certificate model
class DeathCertificate(models.Model):
    deceased = models.OneToOneField(Deceased, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date_issued = models.DateField()
    certificate_number = models.CharField(max_length=100, unique=True, primary_key=True)

    def __str__(self):
        return f'Death Certificate for {self.deceased}'


# Death registration table (with composite primary key of deceased_id and doctor license_id)
class DeathRegistration(models.Model):
    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    registration_date = models.DateField()
    remarks = models.TextField(null=True, blank=True)

    # Foreign key to Disposal table
    disposal_permit = models.ForeignKey(Disposal, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = (('deceased', 'doctor'),)  # Composite primary key

    def __str__(self):
        return f'Registration of {self.deceased.full_name} by Dr. {self.doctor.name}'


# Postmortem table
class Postmortem(models.Model):
    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE)
    pathologist = models.ForeignKey(Pathologist, on_delete=models.CASCADE)
    report = models.TextField()
    date_conducted = models.DateField()

    def __str__(self):
        return f'Postmortem for {self.deceased.full_name}'


# Embalmer's table (with license_id as primary key)
class Embalmer(models.Model):
    license_id = models.CharField(max_length=100, unique=True, primary_key=True)  # Primary Key
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=255)
    deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE)  # Foreign key to deceased
    embalming_details = models.TextField()
    date_of_embalming = models.DateField()
    nrc = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'Embalmer: {self.name} for {self.deceased.full_name}'
