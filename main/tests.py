from datetime import date

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Project, Skill, Tag


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Evan Andrian")
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(
            response,
            f'const BASE_EXPERIENCES_ENDPOINT = "{reverse("main:get_experience_json")}";',
        )
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, 'id="empty"')
        self.assertContains(response, "Belum ada experience yang ditambahkan atau ditemukan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()[0]["fields"]["is_ongoing"])
        self.assertEqual(
            response.json()[0]["fields"]["get_category_display"],
            "Part-Time",
        )


class ModelTest(TestCase):
    def test_create_and_edit_views_share_form_page(self):
        admin = User.objects.create_superuser(
            username="form-admin",
            email="form-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)
        project = Project.objects.create(name="Portfolio", description="A portfolio.")
        experience = Experience.objects.create(title="Internship", description="Worked on a project.")
        education = Education.objects.create(
            name="University",
            description="Computer science degree.",
            started_at=date(2025, 8, 1),
        )
        skill = Skill.objects.create(title="Python")
        form_pages = [
            ("create_project", {}, "show_projects"),
            ("create_experience", {}, "show_experience"),
            ("create_education", {}, "show_education"),
            ("create_skill", {}, "show_skill"),
            ("edit_project", {"project_id": project.id}, "show_projects"),
            ("edit_experience", {"experience_id": experience.id}, "show_experience"),
            ("edit_education", {"education_id": education.id}, "show_education"),
            ("edit_skill", {"skill_id": skill.id}, "show_skill"),
        ]

        for form_route, route_kwargs, cancel_route in form_pages:
            with self.subTest(route=form_route):
                response = self.client.get(
                    reverse(f"main:{form_route}", kwargs=route_kwargs),
                )
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "form_page.html")
                self.assertEqual(
                    response.context["form_action"],
                    reverse(f"main:{form_route}", kwargs=route_kwargs),
                )
                self.assertEqual(
                    response.context["cancel_url"],
                    reverse(f"main:{cancel_route}"),
                )

    def test_all_portfolio_pages_render_the_shared_add_modal(self):
        admin = User.objects.create_superuser(
            username="modal-admin",
            email="modal-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)
        pages = [
            ("show_projects", "add-project-modal", "project-form", "create_project"),
            ("show_experience", "add-experience-modal", "experience-form", "create_experience"),
            ("show_education", "add-education-modal", "education-form", "create_education"),
            ("show_skill", "add-skill-modal", "skill-form", "create_skill"),
        ]

        for page_name, modal_id, form_id, action_name in pages:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(f"main:{page_name}"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'id="{modal_id}"')
                self.assertContains(response, f'id="{form_id}"')
                self.assertContains(
                    response,
                    f'action="{reverse(f"main:{action_name}")}"',
                )
                self.assertContains(response, f'popovertarget="{modal_id}"')

    def test_create_experience_ajax_adds_an_experience(self):
        admin = User.objects.create_superuser(
            username="experience-admin",
            email="experience-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse("main:create_experience_ajax"),
            {
                "title": "Internship",
                "description": "Built useful features.",
                "category": "full-time",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Experience.objects.get().title, "Internship")

    def test_create_project_ajax_adds_a_project(self):
        admin = User.objects.create_superuser(
            username="project-admin",
            email="project-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse("main:create_project_ajax"),
            {
                "name": "Portfolio Website",
                "description": "A personal portfolio.",
            },
        )

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get()
        self.assertEqual(project.name, "Portfolio Website")
        self.assertEqual(response.json()["pk"], str(project.id))

    def test_create_education_ajax_adds_an_education(self):
        admin = User.objects.create_superuser(
            username="education-admin",
            email="education-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)

        response = self.client.post(
            reverse("main:create_education_ajax"),
            {
                "name": "University of Indonesia",
                "degree": "Bachelor of Computer Science",
                "description": "Faculty of Computer Science.",
                "started_at": "2025-08-01",
            },
        )

        self.assertEqual(response.status_code, 201)
        education = Education.objects.get()
        self.assertEqual(education.name, "University of Indonesia")
        self.assertEqual(response.json()["pk"], str(education.id))

    def test_ajax_create_endpoints_reject_non_superusers(self):
        user = User.objects.create_user(
            username="portfolio-user",
            password="test-password",
        )
        self.client.force_login(user)
        endpoints = [
            (
                "create_project_ajax",
                {"name": "Portfolio", "description": "A portfolio."},
                Project,
            ),
            (
                "create_experience_ajax",
                {"title": "Internship", "description": "Built useful features."},
                Experience,
            ),
            (
                "create_education_ajax",
                {
                    "name": "University",
                    "description": "Computer science degree.",
                    "started_at": "2025-08-01",
                },
                Education,
            ),
            ("create_skill_ajax", {"title": "Python"}, Skill),
        ]

        for route_name, data, model in endpoints:
            with self.subTest(route=route_name):
                response = self.client.post(reverse(f"main:{route_name}"), data)

                self.assertEqual(response.status_code, 403)
                self.assertFalse(model.objects.exists())

    def test_skill_page_renders_search_controls_used_by_script(self):
        response = self.client.get(reverse("main:show_skill"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="skill-search-form"')
        self.assertContains(response, 'id="search-input"')
        self.assertContains(response, "getElementById('skill-search-form')")
        self.assertContains(response, "getElementById('search-input')")

    def test_skill_json_includes_tags_and_filters_by_name(self):
        matching_skill = Skill.objects.create(title="Programming Languages")
        other_skill = Skill.objects.create(title="Design")
        python = Tag.objects.create(name="Python")
        matching_skill.tags.add(python)

        response = self.client.get(
            reverse("main:get_skill_json"),
            {"name": "programming"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "pk": str(matching_skill.id),
                    "fields": {
                        "title": "Programming Languages",
                        "tags": ["Python"],
                        "star_count": 0,
                        "is_starred": False,
                        "starred_by_names": "",
                    },
                }
            ],
        )
        self.assertNotIn(str(other_skill.id), response.content.decode())

    def test_create_skill_ajax_saves_selected_tags(self):
        admin = User.objects.create_superuser(
            username="skill-admin",
            email="skill-admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)
        tag = Tag.objects.create(name="Django")

        response = self.client.post(
            reverse("main:create_skill_ajax"),
            {"title": "Frameworks", "tags": [str(tag.id)]},
        )

        self.assertEqual(response.status_code, 201)
        skill = Skill.objects.get(title="Frameworks")
        self.assertEqual(list(skill.tags.all()), [tag])

    def test_experience_json_includes_card_display_fields(self):
        experience = Experience.objects.create(
            title="Research Assistant",
            description="Conducted research.",
            category="part-time",
        )

        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0]["fields"]["get_category_display"],
            "Part-Time",
        )
        self.assertTrue(response.json()[0]["fields"]["is_ongoing"])
        self.assertEqual(response.json()[0]["pk"], str(experience.id))

    def test_project_page_uses_project_edit_permission_for_controls(self):
        user = User.objects.create_user(
            username="project-editor",
            password="test-password",
        )
        project_edit_permission = Permission.objects.get(
            content_type__app_label="main",
            codename="change_project",
        )
        user.user_permissions.add(project_edit_permission)
        self.client.force_login(user)

        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'const EDITOR = "true" === "true";')

    def test_delete_modal_renders_correct_route_for_each_model(self):
        admin = User.objects.create_superuser(
            username="modal-admin",
            email="admin@example.com",
            password="test-password",
        )
        self.client.force_login(admin)
        targets = [
            (
                "show_projects",
                "delete_project",
                Project.objects.create(name="Portfolio Website", description="A portfolio."),
            ),
            (
                "show_experience",
                "delete_experience",
                Experience.objects.create(title="Research Assistant", description="Conducted research."),
            ),
            (
                "show_education",
                "delete_education",
                Education.objects.create(
                    name="University of Indonesia",
                    description="Computer science degree.",
                    started_at=date(2025, 8, 1),
                ),
            ),
            ("show_skill", "delete_skill", Skill.objects.create(title="Python")),
        ]

        for page_name, delete_name, item in targets:
            with self.subTest(model=delete_name):
                response = self.client.get(reverse(f"main:{page_name}"))
                self.assertEqual(response.status_code, 200)
                delete_url_template = reverse(
                    f"main:{delete_name}",
                    args=["00000000-0000-0000-0000-000000000000"],
                )
                self.assertContains(response, f'const deleteUrl = "{delete_url_template}"')
                self.assertContains(
                    response,
                    ".replace('00000000-0000-0000-0000-000000000000',",
                )

                delete_response = self.client.post(
                    reverse(f"main:{delete_name}", args=[item.id]),
                )
                self.assertRedirects(delete_response, reverse(f"main:{page_name}"))
                self.assertFalse(type(item).objects.filter(pk=item.id).exists())

    def test_toggle_star_supports_all_starable_models(self):
        user = User.objects.create_user(username="star-user", password="test-password")
        self.client.force_login(user)
        targets = [
            (
                "toggle_project_star",
                Project.objects.create(name="Portfolio", description="A portfolio."),
            ),
            (
                "toggle_experience_star",
                Experience.objects.create(title="Internship", description="Worked on a project."),
            ),
            (
                "toggle_education_star",
                Education.objects.create(
                    name="University",
                    description="Computer science degree.",
                    started_at=date(2025, 8, 1),
                ),
            ),
            ("toggle_skill_star", Skill.objects.create(title="Python")),
        ]

        for route_name, item in targets:
            with self.subTest(model=route_name):
                response = self.client.post(reverse(f"main:{route_name}", args=[item.id]))
                self.assertEqual(response.status_code, 302)
                self.assertTrue(item.starred_by.filter(pk=user.pk).exists())

                self.client.post(reverse(f"main:{route_name}", args=[item.id]))
                self.assertFalse(item.starred_by.filter(pk=user.pk).exists())

    def test_toggle_star_rejects_get_requests(self):
        user = User.objects.create_user(username="star-user", password="test-password")
        self.client.force_login(user)
        project = Project.objects.create(name="Portfolio", description="A portfolio.")

        response = self.client.get(
            reverse("main:toggle_project_star", args=[project.id]),
        )

        self.assertEqual(response.status_code, 405)
        self.assertFalse(project.starred_by.filter(pk=user.pk).exists())

    def test_experience_json_filters_by_requested_name(self):
        matching = Experience.objects.create(
            title="Research Assistant",
            description="Conducted research.",
        )
        Experience.objects.create(title="Teaching Assistant", description="Helped students.")

        response = self.client.get(reverse("main:get_experience_json"), {"name": "research"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["pk"] for item in response.json()], [str(matching.id)])

    def test_education_json_filters_by_requested_name(self):
        matching = Education.objects.create(
            name="University of Indonesia",
            description="Computer science degree.",
            started_at=date(2025, 8, 1),
        )
        Education.objects.create(
            name="High School",
            description="Secondary education.",
            started_at=date(2021, 7, 1),
        )

        response = self.client.get(reverse("main:get_education_json"), {"name": "university"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["pk"] for item in response.json()], [str(matching.id)])
        self.assertEqual(response.json()[0]["fields"]["year_range"], "2025 — Present")
        self.assertEqual(response.json()[0]["fields"]["degree"], "")

    def test_experience_defaults_and_string(self):
        experience = Experience.objects.create(
            title="Research Assistant",
            description="Conducted research.",
        )

        self.assertEqual(str(experience), "Research Assistant")
        self.assertEqual(experience.category, "full-time")
        self.assertIsNone(experience.thumbnail)
        self.assertTrue(experience.is_ongoing)

    def test_tag_string(self):
        tag = Tag.objects.create(name="Django")

        self.assertEqual(str(tag), "Django")

    def test_projects_api_includes_tags_and_filters_by_name(self):
        matching_project = Project.objects.create(
            name="Portfolio Website",
            description="A personal portfolio.",
        )
        other_project = Project.objects.create(
            name="Weather App",
            description="A weather application.",
        )
        tag = Tag.objects.create(name="Django")
        matching_project.tags.add(tag)

        response = self.client.get(
            reverse("main:get_projects_json"),
            {"name": "portfolio"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "pk": str(matching_project.id),
                    "fields": {
                        "name": "Portfolio Website",
                        "description": "A personal portfolio.",
                        "tags": ["Django"],
                        "project_url": "",
                        "project_image_url": "",
                        "star_count": 0,
                        "is_starred": False,
                        "starred_by_names": "",
                    },
                }
            ],
        )
        self.assertNotIn(str(other_project.id), response.content.decode())

    def test_project_string_and_tags(self):
        project = Project.objects.create(
            name="Portfolio",
            description="A personal portfolio.",
        )
        tag = Tag.objects.create(name="Django")
        project.tags.add(tag)

        self.assertEqual(str(project), "Portfolio")
        self.assertEqual(list(project.tags.all()), [tag])
        self.assertEqual(list(tag.projects.all()), [project])

    def test_education_ongoing_string_and_year_range(self):
        education = Education.objects.create(
            name="Universitas Indonesia",
            description="Computer science degree.",
            started_at=date(2025, 8, 1),
        )

        self.assertEqual(str(education), "Universitas Indonesia")
        self.assertTrue(education.is_ongoing)
        self.assertEqual(education.year_range, "2025 — Present")

    def test_completed_education_year_range(self):
        education = Education.objects.create(
            name="High School",
            description="Secondary education.",
            started_at=date(2021, 7, 1),
            ended_at=date(2024, 6, 30),
        )

        self.assertFalse(education.is_ongoing)
        self.assertEqual(education.year_range, "2021 — 2024")

    def test_skill_string_and_tags(self):
        skill = Skill.objects.create(title="Python")
        tag = Tag.objects.create(name="Backend")
        skill.tags.add(tag)

        self.assertEqual(str(skill), "Python")
        self.assertEqual(list(skill.tags.all()), [tag])
        self.assertEqual(list(tag.skills.all()), [skill])