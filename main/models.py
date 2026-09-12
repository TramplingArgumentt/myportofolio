import uuid
from django.db import models
from datetime import date

def current_year():
    return date.today().year

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    year = models.IntegerField(default=current_year)
    affiliation = models.TextField()
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    tags = models.ManyToManyField(Tag, blank=True, related_name='projects')
    category = models.CharField(max_length=255)
    url = models.TextField(blank=True)
    def __str__(self):
        return self.name
    
class Education(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name
    
    @property
    def is_ongoing(self):
        return self.ended_at is None
    
    @property
    def year_range(self):
        end = "Present" if self.is_ongoing else self.ended_at.year
        return f"{self.started_at.year} — {end}"

class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, blank=True, related_name='skills')

    def __str__(self):
        return self.title