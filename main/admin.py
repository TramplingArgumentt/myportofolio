from django.contrib import admin

from .models import Experience, Project, Education, Skill, Tag

admin.site.register(Experience)
admin.site.register(Project)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Tag)