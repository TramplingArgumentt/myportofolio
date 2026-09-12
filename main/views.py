from django.shortcuts import render

from main.models import Experience, Project, Education, Skill, Tag

def show_main(request):
    context = {
        "name": "Evan Andrian",
        "npm": "2506539082",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "CS student at Universitas Indonesia, often seen at Kantin Pacil on lunch time."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    context = {
        "name": "Evan Andrian",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_project(request):
    context = {
        "name": "Evan Andrian",
        "project_list": Project.objects.all(),
        "tag_list": Tag.objects.all(),
    }
    return render(request, "project.html", context)

def show_education(request):
    context = {
        "name": "Evan Andrian",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def show_skill(request):
    context = {
        "name": "Evan Andrian",
        "skill_list": Skill.objects.all(),
        "tag_list": Tag.objects.all(),
    }
    return render(request, "skill.html", context)