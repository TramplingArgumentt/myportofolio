from django.forms import DateInput, DateTimeInput, ModelForm, Select, TextInput, Textarea, URLInput
from django import forms
from main.models import Project, Experience, Education, Skill

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "tags",
            "project_url",
            "project_image_url",
        ]

        labels = {
            "name": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tags": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "tags": forms.CheckboxSelectMultiple(
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/kakBurhan/burhanquestv4",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

class ExperienceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and self.instance._state.adding:
            self.initial.setdefault("category", self.instance.category)

    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]

        labels = {
            "title": "Nama Experience",
            "description": "Deskripsi Experience",
            "category": "Tipe Experience",
            "started_at": "Tanggal Dimulai",
            "ended_at": "Tanggal Selesai",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Personal Portofolio",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Pengalamanmu",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "started_at": DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
            "ended_at": DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

class EducationForm(ModelForm):
    class Meta:
        model = Education
        fields = [
            "name",
            "degree",
            "description",
            "started_at",
            "ended_at",
        ]

        labels = {
            "name": "Nama Institusi",
            "degree": "Gelar",
            "description": "Deskripsi Pendidikan",
            "started_at": "Tanggal Dimulai",
            "ended_at": "Tanggal Selesai",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "degree": TextInput(
                attrs={
                    "placeholder": "Bachelor of Computer Science",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Fakultas Ilmu Komputer",
                    "rows": 3,
                    "maxlength": 255,
                }
            ),
            "started_at": DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
            "ended_at": DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            ),
        }

class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = [
            "title",
            "tags",
        ]

        labels = {
            "title": "Tipe Keahlian",
            "tags": "Teknologi yang Dikuasai",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Languages",
                    "maxlength": 255,
                }
            ),
            "tags": forms.CheckboxSelectMultiple(
            ),
        }