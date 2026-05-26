from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class LoanApplication(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    
    
    text_feature = models.TextField()
    f1_income = models.FloatField()
    f2_amount = models.FloatField()
    f3_duration = models.FloatField()
    f4_credit_score = models.FloatField()
    
    
    prediction_result = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ombi la {self.user.username} - Matokeo: {self.prediction_result}"

