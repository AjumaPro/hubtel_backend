from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class KYCSubmission(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PENDING', 'Pending'),
    ]
    
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    data = models.JSONField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"KYCSubmission(id={self.id}, user={self.user}, status={self.status}, submitted_at={self.submitted_at})"


class ContactFormSubmission(models.Model):
    """Model for storing contact form submissions"""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Contact from {self.name} ({self.email}) - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"
