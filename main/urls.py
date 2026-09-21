from django.urls import path

from main.views import show_main, show_experience, show_projects, show_education, show_skill, create_project, get_projects_json, delete_project, create_experience, get_experience_json, delete_experience, create_education, get_education_json, delete_education, create_skill, get_skill_json, delete_skill, edit_project, edit_experience, edit_education, edit_skill

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("education/", show_education, name="show_education"),
    path("skill/", show_skill, name="show_skill"),

    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("projects/<uuid:project_id>/edit/", edit_project, name="edit_project"),

    path("experience/add/", create_experience, name="create_experience"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("experience/<uuid:experience_id>/edit/", edit_experience, name="edit_experience"),

    path("education/add/", create_education, name="create_education"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("education/<uuid:education_id>/edit/", edit_education, name="edit_education"),

    path("skill/add/", create_skill, name="create_skill"),
    path("api/skill/", get_skill_json, name="get_skill_json"),
    path("skill/<uuid:skill_id>/delete/", delete_skill, name="delete_skill"),
    path("skill/<uuid:skill_id>/edit/", edit_skill, name="edit_skill"),
]