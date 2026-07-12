from django.db import models

class Assignment(models.Model):
    file = models.FileField(upload_to="assignments/")
    feedback = models.TextField(blank=True)
    score = models.IntegerField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Assignment {self.id}"

# Create your models here.
