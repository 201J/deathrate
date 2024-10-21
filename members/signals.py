from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Deceased, DeathCertificate,DeathRegistration
from django.utils.crypto import get_random_string

# Auto-generate death certificate when a deceased record is created
@receiver(post_save, sender=Deceased)
def create_death_certificate(sender, instance, created, **kwargs):
    if created:
        # Generate a unique certificate number
        certificate_number = get_random_string(10)  # You can modify this to follow any number generation pattern
        DeathCertificate.objects.create(
            deceased=instance,
            certificate_number=certificate_number,
            # Add the issuing doctor here based on logic
        )


@receiver(post_save, sender=DeathRegistration)
def create_or_update_deceased(sender, instance, created, **kwargs):
    if created:
        # Create a new Deceased entry whenever a new DeathRegistration is created
        Deceased.objects.create(
            full_name=instance.full_name,
            date_of_death=instance.date_of_death,
            cause_of_death=instance.cause_of_death
        )
    else:
        # Update existing Deceased entry if the DeathRegistration is updated
        deceased = Deceased.objects.get(id=instance.deceased.id)
        deceased.full_name = instance.full_name
        deceased.date_of_death = instance.date_of_death
        deceased.cause_of_death = instance.cause_of_death
        deceased.save()