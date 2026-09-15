from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ProjectForm
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

def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("tags").all()

    if title_query:
        projects = projects.filter(name__icontains=title_query)

    context = {
        "name": "Evan Andrian",
        "project_list": projects,
        "title_query": title_query,
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

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "projects_form.html", context)

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related("tags").all()

    if title_query:
        projects = projects.filter(name__icontains=title_query)

    projects_json = serializers.serialize(
        "json",
        projects,
        use_natural_foreign_keys=True,
    )

    return HttpResponse(projects_json, content_type="application/json")

def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")