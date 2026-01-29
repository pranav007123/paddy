from django.db import models

class user(models.Model):
    name=models.CharField(max_length=150)
    phone_number=models.CharField(max_length=120)
    email=models.CharField(max_length=120)
    password=models.CharField(max_length=120)
    confirm_password=models.CharField(max_length=120)
    is_superuser=models.BooleanField(default=False)

class fileupload(models.Model):
    userid=models.CharField(max_length=150)
    file=models.FileField(max_length=200)
    result=models.CharField(max_length=120)

# class officer(models.Model):
#     officer_name=models.CharField(max_length=150)
#     phone_number=models.CharField(max_length=120)
#     place=models.CharField(max_length=150)

# class bookings(models.Model):
#     officer_name=models.CharField(max_length=150)
#     officer_id=models.CharField(max_length=150)
#     date=models.CharField(max_length=150)
#     time=models.CharField(max_length=150)
#     status=models.CharField(max_length=150)

# class results(models.Model):
#     heading=models.CharField(max_length=150)
#     description=models.CharField(max_length=150)
#     solution=models.CharField(max_length=150)

