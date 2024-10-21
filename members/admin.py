from django.contrib import admin
from .models import Deceased, Pathologist, Doctor,Disposal, DeathCertificate, Postmortem, Embalmer,DeathRegistration,Notification

# Register your models here.
admin.site.register(Deceased)
admin.site.register(Pathologist)
admin.site.register(Doctor)
admin.site.register(DeathCertificate)
admin.site.register(Postmortem)
admin.site.register(Embalmer)
admin.site.register(Disposal)
admin.site.register(DeathRegistration)
admin.site.register(Notification)
