from django.urls import path

from main.views import (show_main, show_experience, show_projects, show_education, show_skill,
                        create_project, get_projects_json, delete_item,
                        create_experience, get_experience_json,
                        create_education, get_education_json,
                        create_skill, get_skill_json,
                        edit_project, edit_experience, edit_education, edit_skill, 
                        register, login_user, logout_user, toggle_star, create_project_ajax,
                        create_experience_ajax, create_education_ajax, create_skill_ajax)

app_name = "main"

urlpatterns = [

    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("projects/", show_projects, name="show_projects"),
    path("education/", show_education, name="show_education"),
    path("skill/", show_skill, name="show_skill"),

    path("projects/add/", create_project, name="create_project"),
    path("projects/add-ajax/", create_project_ajax, name="create_project_ajax"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("projects/<uuid:object_id>/delete/", delete_item, {"model_type": "project"}, name="delete_project"),
    path("projects/<uuid:project_id>/edit/", edit_project, name="edit_project"),
    path("projects/<uuid:object_id>/star/", toggle_star, {"model_type": "project"}, name="toggle_project_star"),

    path("experience/add/", create_experience, name="create_experience"),
    path("experience/add-ajax/", create_experience_ajax, name="create_experience_ajax"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("experience/<uuid:object_id>/delete/", delete_item, {"model_type": "experience"}, name="delete_experience"),
    path("experience/<uuid:experience_id>/edit/", edit_experience, name="edit_experience"),
    path("experience/<uuid:object_id>/star/", toggle_star, {"model_type": "experience"}, name="toggle_experience_star"),

    path("education/add/", create_education, name="create_education"),
    path("education/add-ajax/", create_education_ajax, name="create_education_ajax"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("education/<uuid:object_id>/delete/", delete_item, {"model_type": "education"}, name="delete_education"),
    path("education/<uuid:education_id>/edit/", edit_education, name="edit_education"),
    path("education/<uuid:object_id>/star/", toggle_star, {"model_type": "education"}, name="toggle_education_star"),

    path("skill/add/", create_skill, name="create_skill"),
    path("skill/add-ajax/", create_skill_ajax, name="create_skill_ajax"),
    path("api/skill/", get_skill_json, name="get_skill_json"),
    path("skill/<uuid:object_id>/delete/", delete_item, {"model_type": "skill"}, name="delete_skill"),
    path("skill/<uuid:skill_id>/edit/", edit_skill, name="edit_skill"),
    path("skill/<uuid:object_id>/star/", toggle_star, {"model_type": "skill"}, name="toggle_skill_star"),
]