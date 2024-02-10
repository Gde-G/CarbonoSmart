from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class Company(models.Model):
    name = models.CharField(max_length=150)
    website = models.CharField(max_length=200, null=True, blank=True)
    contact_name = models.CharField(max_length=150)
    contact_email = models.EmailField()
    country = models.ForeignKey(
        'cities_light.country', on_delete=models.CASCADE)
    contact_phone = PhoneNumberField(null=True, blank=True)
    topic_about = models.CharField(max_length=200)
    content = models.TextField()
    date_make = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}, make by {self.contact_name}"
