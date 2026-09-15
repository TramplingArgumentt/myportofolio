from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date

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
        self.assertNotContains(response, self.experience.title)
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

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Part-Time")
        self.assertNotContains(response, "Sedang berlangsung")


class ModelTest(TestCase):
    def test_experience_defaults_and_string(self):
        experience = Experience.objects.create(
            title="Research Assistant",
            affiliation="Universitas Indonesia",
            description="Conducted research.",
        )

        self.assertEqual(str(experience), "Research Assistant")
        self.assertEqual(experience.year, date.today().year)
        self.assertEqual(experience.category, "full-time")
        self.assertIsNone(experience.thumbnail)
        self.assertTrue(experience.is_ongoing)

    def test_tag_string(self):
        tag = Tag.objects.create(name="Django")

        self.assertEqual(str(tag), "Django")

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