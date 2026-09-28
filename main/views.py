from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from main.forms import EducationForm, ExperienceForm, ProjectForm, SkillForm
from main.models import Experience, Project, Education, Skill
import datetime

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Evan Andrian",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Evan Andrian",
        "npm": "2506539082",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "CS student at Universitas Indonesia, often seen at Kantin Pacil on lunch time."
        ),
        "last_login": last_login,
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

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
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

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
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

@login_required(login_url="/login/")
def create_education(request):
    if not request.user.is_superuser:
        raise PermissionDenied
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

@login_required(login_url="/login/")
def create_skill(request):
    if not request.user.is_superuser:
        raise PermissionDenied
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
        experience = experience.filter(title__icontains=name_query)

    experiences_json = serializers.serialize(
        "json", 
        experience,
        use_natural_foreign_keys=True,
    )
    return HttpResponse(experiences_json, content_type="application/json")

def get_education_json(request):
    name_query = request.GET.get("name", "").strip()
    education = Education.objects.all()

    if name_query:
        education = education.filter(name__icontains=name_query)

    education_json = serializers.serialize(
        "json",
        education,
        use_natural_foreign_keys=True,
    )
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

@login_required(login_url="/login/")
def delete_item(request, model_type, object_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    item_targets = {
        "project": (Project, "main:show_projects"),
        "experience": (Experience, "main:show_experience"),
        "education": (Education, "main:show_education"),
        "skill": (Skill, "main:show_skill"),
    }

    target = item_targets.get(model_type)
    if target is None:
        raise Http404
    
    model, redirect_name = target
    item = get_object_or_404(model, pk=object_id)

    if request.method == "POST":
        item.delete()
        messages.success(request, f"{model.__name__} berhasil dihapus!")
        return redirect(redirect_name)

    return redirect(redirect_name)

@login_required(login_url="/login/")
@permission_required('main.change_project', raise_exception=True)
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project berhasil diedit!")
            return redirect('main:show_projects')
    else:
        form = ProjectForm(instance=project)

    context = {
        "name": "Evan Andrian",
        "form": form,
        "project": project,
    }

    return render(request, "edit_project.html", context)

@login_required(login_url="/login/")
@permission_required('main.change_experience', raise_exception=True)
def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Experience berhasil diedit!")
            return redirect('main:show_experience')
    else:
        form = ExperienceForm(instance=experience)

    context = {
        "name": "Evan Andrian",
        "form": form,
        "experience": experience,
    }

    return render(request, "edit_experience.html", context)

@login_required(login_url="/login/")
@permission_required('main.change_education', raise_exception=True)
def edit_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Education berhasil diedit!")
            return redirect('main:show_education')
    else:
        form = EducationForm(instance=education)

    context = {
        "name": "Evan Andrian",
        "form": form,
        "education": education,
    }

    return render(request, "edit_education.html", context)

@login_required(login_url="/login/")
@permission_required('main.change_skill', raise_exception=True)
def edit_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, "Skill berhasil diedit!")
            return redirect('main:show_skill')
    else:
        form = SkillForm(instance=skill)

    context = {
        "name": "Evan Andrian",
        "form": form,
        "skill": skill,
    }

    return render(request, "edit_skill.html", context)

@login_required(login_url="/login/")
@require_POST
def toggle_star(request, model_type, object_id):
    star_targets = {
        "project": (Project, "main:show_projects"),
        "experience": (Experience, "main:show_experience"),
        "education": (Education, "main:show_education"),
        "skill": (Skill, "main:show_skill"),
    }
    target = star_targets.get(model_type)
    if target is None:
        raise Http404

    model, redirect_name = target
    item = get_object_or_404(model, pk=object_id)

    if request.method == "POST":
        if request.user in item.starred_by.all():
            item.starred_by.remove(request.user)
        else:
            item.starred_by.add(request.user)

    return redirect(redirect_name)