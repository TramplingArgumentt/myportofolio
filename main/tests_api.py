import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Experience, Project, Skill


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password",
            email="owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="visitor", password="test-password",
        )
        self.project = Project.objects.create(
            name="Portfolio", description="My website",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "name": "New project", "description": "A useful app", "tags": [],
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(
            self.client.get(self.detail_url).status_code, status.HTTP_200_OK,
        )

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"name": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"name": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(
            self.client.get(url).status_code, status.HTTP_404_NOT_FOUND,
        )

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(
                    self.list_url, self.payload, format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"name": "Changed"}, format="json",
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Portfolio")

    def test_owner_create_validation_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url, self.payload, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())
        response = self.client.patch(
            self.detail_url, {"name": "Changed"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(
            self.detail_url, {"name": "Incomplete"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for changes, field in [
            ({"name": "   "}, "name"),
            ({"name": '<img src="x" onerror="alert(1)">'} , "name"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(
            self.detail_url, {"name": "Changed"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post(
                self.list_url, self.payload, format="json",
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(
            self.client.delete(self.list_url).status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(
            username="owner", password="test-password",
        ))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(
            username="owner", password="test-password",
        ))
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PortfolioSectionAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="section-owner", password="test-password",
            email="section-owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="section-visitor", password="test-password",
        )
        editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(
            username="section-editor", password="test-password",
        )
        self.editor.groups.add(editor_group)
        self.sections = [
            {
                "model": Education,
                "list": "api:education-list",
                "detail": "api:education-detail",
                "star": "api:education-star",
                "payload": {
                    "name": "University", "degree": "BSc",
                    "description": "Computer science.",
                    "started_at": "2022-09-01", "ended_at": None,
                },
                "search": "name",
                "edit_field": "name",
            },
            {
                "model": Experience,
                "list": "api:experience-list",
                "detail": "api:experience-detail",
                "star": "api:experience-star",
                "payload": {
                    "title": "Developer", "description": "Built software.",
                    "category": "full-time", "thumbnail": None,
                    "started_at": None, "ended_at": None,
                },
                "search": "title",
                "edit_field": "title",
            },
            {
                "model": Skill,
                "list": "api:skill-list",
                "detail": "api:skill-detail",
                "star": "api:skill-star",
                "payload": {"title": "Python", "tags": []},
                "search": "title",
                "edit_field": "title",
            },
        ]

    def create_item(self, section):
        payload = section["payload"].copy()
        tags = payload.pop("tags", None)
        item = section["model"].objects.create(**payload)
        if tags is not None:
            item.tags.set(tags)
        return item

    def test_owner_create_and_delete_for_each_section(self):
        self.client.force_authenticate(user=self.owner)
        for section in self.sections:
            with self.subTest(section=section["model"].__name__):
                response = self.client.post(
                    reverse(section["list"]), section["payload"], format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                item_id = response.data["id"]
                self.assertTrue(
                    section["model"].objects.filter(pk=item_id).exists(),
                )
                response = self.client.delete(reverse(
                    section["detail"], args=[item_id],
                ))
                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
                self.assertFalse(
                    section["model"].objects.filter(pk=item_id).exists(),
                )

    def test_visitors_cannot_write_to_any_section(self):
        for section in self.sections:
            with self.subTest(section=section["model"].__name__):
                item = self.create_item(section)
                list_url = reverse(section["list"])
                detail_url = reverse(section["detail"], args=[item.pk])
                for user in (None, self.visitor):
                    self.client.force_authenticate(user=user)
                    self.assertEqual(
                        self.client.post(
                            list_url, section["payload"], format="json",
                        ).status_code,
                        status.HTTP_403_FORBIDDEN,
                    )
                    self.assertEqual(
                        self.client.patch(
                            detail_url,
                            {section["edit_field"]: "Changed"},
                            format="json",
                        ).status_code,
                        status.HTTP_403_FORBIDDEN,
                    )
                    self.assertEqual(
                        self.client.delete(detail_url).status_code,
                        status.HTTP_403_FORBIDDEN,
                    )
                self.assertEqual(section["model"].objects.count(), 1)
                item.refresh_from_db()
                self.assertEqual(
                    getattr(item, section["edit_field"]),
                    section["payload"][section["edit_field"]],
                )

    def test_editor_can_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)
        for section in self.sections:
            with self.subTest(section=section["model"].__name__):
                item = self.create_item(section)
                list_url = reverse(section["list"])
                detail_url = reverse(section["detail"], args=[item.pk])
                response = self.client.patch(
                    detail_url, {section["edit_field"]: "Changed"}, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                item.refresh_from_db()
                self.assertEqual(getattr(item, section["edit_field"]), "Changed")
                self.assertEqual(
                    self.client.post(
                        list_url, section["payload"], format="json",
                    ).status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    self.client.delete(detail_url).status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(section["model"].objects.count(), 1)

    def test_lists_search_and_stars_for_each_section(self):
        self.client.force_authenticate(user=self.visitor)
        for section in self.sections:
            with self.subTest(section=section["model"].__name__):
                item = self.create_item(section)
                list_url = reverse(section["list"])
                response = self.client.get(list_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data[0]["id"], str(item.pk))
                self.assertFalse(response.data[0]["is_starred"])
                detail_response = self.client.get(
                    reverse(section["detail"], args=[item.pk]),
                )
                self.assertEqual(
                    detail_response.status_code, status.HTTP_200_OK,
                )
                self.assertEqual(detail_response.data["id"], str(item.pk))
                search_value = section["payload"][section["search"]]
                self.assertEqual(
                    len(self.client.get(list_url, {"name": search_value}).data),
                    1,
                )
                self.assertEqual(
                    self.client.get(list_url, {"name": "missing"}).data, [],
                )
                star_url = reverse(section["star"], args=[item.pk])
                self.assertTrue(self.client.post(star_url).data["is_starred"])
                self.assertFalse(self.client.post(star_url).data["is_starred"])
                self.client.force_authenticate(user=None)
                self.assertEqual(
                    self.client.post(star_url).status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.client.force_authenticate(user=self.visitor)

    def test_text_validation_strips_tags_and_rejects_empty_titles(self):
        self.client.force_authenticate(user=self.owner)
        for section in self.sections:
            with self.subTest(section=section["model"].__name__):
                payload = section["payload"].copy()
                field = section["edit_field"]
                payload[field] = "   "
                response = self.client.post(
                    reverse(section["list"]), payload, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                payload[field] = "<b>Clean title</b>"
                response = self.client.post(
                    reverse(section["list"]), payload, format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                item = section["model"].objects.get(pk=response.data["id"])
                self.assertEqual(getattr(item, field), "Clean title")

    def test_session_write_requires_csrf_for_each_section(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(
            username="section-owner", password="test-password",
        ))
        for section in self.sections:
            with self.subTest(section=section["model"].__name__):
                list_url = reverse(section["list"])
                response = client.post(
                    list_url, section["payload"], format="json",
                )
                self.assertEqual(
                    response.status_code, status.HTTP_403_FORBIDDEN,
                )
                self.assertFalse(section["model"].objects.exists())

                page = client.get(list_url, HTTP_ACCEPT="text/html")
                self.assertEqual(page.status_code, status.HTTP_200_OK)
                response = client.post(
                    list_url,
                    section["payload"],
                    format="json",
                    HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
                )
                self.assertEqual(
                    response.status_code, status.HTTP_201_CREATED,
                )
