from django.shortcuts import render

from main.models import Experience

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