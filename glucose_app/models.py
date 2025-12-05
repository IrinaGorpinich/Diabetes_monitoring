from django.db import models

from django.contrib.auth.models import User

class GlucoseRecord(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.CharField(max_length=100)
    glucose = models.FloatField()
    unit = models.CharField(max_length=10, default="mmol")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "glucose_records"

class FoodIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    calories = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "food_intake"