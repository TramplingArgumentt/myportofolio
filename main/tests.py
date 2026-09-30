from datetime import date

from django.contrib.auth.models import User
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
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada experience yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Part-Time")
        self.assertNotContains(response, "Sedang berlangsung")


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
                self.assertContains(
                    response,
                    f'action="{reverse(f"main:{delete_name}", args=[item.id])}"',
                )
                self.assertContains(response, f'popovertarget="delete-{item.id}"')

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