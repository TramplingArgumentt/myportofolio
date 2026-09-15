from django.urls import path

from main.views import show_main, show_experience, show_projects, show_education, show_skill, create_project, get_projects_json

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("education/", show_education, name="show_education"),
    path("skill/", show_skill, name="show_skill"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json")
]