from django.db import models
from django.db import models

class Career(models.Model):
    name = models.CharField(max_length=100)
    interest = models.CharField(max_length=100)
    suggested_career = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Assignment(models.Model):
    file_name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name

# Create your models here.
