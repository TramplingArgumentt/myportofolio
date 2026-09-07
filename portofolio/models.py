from django.db import models
from django.utils import timezone
from datetime import datetime

class Mahasiswa(models.Model):    
    name = models.CharField(max_length=30)   
    npm = models.CharField(max_length=10)

class Post(models.Model):   
    author = models.ForeignKey(Mahasiswa, on_delete = models.CASCADE)   
    content = models.CharField(max_length=125)   
    published_date = models.DateTimeField(default=timezone.now)