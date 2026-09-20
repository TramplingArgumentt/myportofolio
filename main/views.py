from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import EducationForm, ExperienceForm, ProjectForm, SkillForm
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
    name_query = request.GET.get("name", "").strip()
    experience = Experience.objects.all()

    if name_query:
        experience = experience.filter(title__icontains=name_query)

    context = {
        "name": "Evan Andrian",
        "experience_list": experience,
        "name_query": name_query,
    }
    return render(request, "experience.html", context)

def show_projects(request):
    name_query = request.GET.get("name", "").strip()
    projects = Project.objects.prefetch_related("tags").all()

    if name_query:
        projects = projects.filter(name__icontains=name_query)

    context = {
        "name": "Evan Andrian",
        "project_list": projects,
        "name_query": name_query,
    }
    return render(request, "project.html", context)

def show_education(request):
    name_query = request.GET.get("name", "").strip()
    education = Education.objects.all()

    if name_query:
        education = education.filter(name__icontains=name_query)

    context = {
        "name": "Evan Andrian",
        "education_list": education,
        "name_query": name_query,
    }
    return render(request, "education.html", context)

def show_skill(request):
    name_query = request.GET.get("name", "").strip()
    skill = Skill.objects.prefetch_related("tags").all()

    if name_query:
        skill = skill.filter(title__icontains=name_query)

    context = {
        "name": "Evan Andrian",
        "skill_list": skill,
        "name_query": name_query,
    }
    return render(request, "skill.html", context)

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def create_experience(request):
    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Experience baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "experience_form.html", context)

def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education baru berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "education_form.html", context)

def create_skill(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Skill baru berhasil ditambahkan!")
        return redirect("main:show_skill")

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "skill_form.html", context)

def get_projects_json(request):
    name_query = request.GET.get("name", "").strip()
    projects = Project.objects.prefetch_related("tags").all()

    if name_query:
        projects = projects.filter(name__icontains=name_query)

    projects_json = serializers.serialize(
        "json",
        projects,
        use_natural_foreign_keys=True,
    )

    return HttpResponse(projects_json, content_type="application/json")

def get_experience_json(request):
    name_query = request.GET.get("name", "").strip()
    experience = Experience.objects.all()

    if name_query:
        experience = experience.filter(title__icontains="name_query")

    experiences_json = serializers.serialize("json", Experience.objects.all())
    return HttpResponse(experiences_json, content_type="application/json")

def get_education_json(request):
    name_query = request.GET.get("name", "").strip()
    education = Education.objects.all()

    if name_query:
        education = education.filter(name__icontains="name_query")

    education_json = serializers.serialize("json", Education.objects.all())
    return HttpResponse(education_json, content_type="application/json")

def get_skill_json(request):
    name_query = request.GET.get("name", "").strip()
    skill = Skill.objects.prefetch_related("tags").all()

    if name_query:
        skill = skill.filter(title__icontains=name_query)

    skill_json = serializers.serialize(
        "json",
        skill,
        use_natural_foreign_keys=True,
    )

    return HttpResponse(skill_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Education berhasil dihapus!")
        return redirect("main:show_education")

    return redirect("main:show_education")

def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        skill.delete()
        messages.success(request, "Skill berhasil dihapus!")
        return redirect("main:show_skill")

    return redirect("main:show_skill")