from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Experience, Project, Skill, Tag


class TagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return value.name


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProjectSerializer(serializers.ModelSerializer):
    tags = TagPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False,
    )
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "name", "description", "tags",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class StarredModelSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return obj.starred_by.filter(pk=request.user.pk).exists()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(StarredModelSerializer):
    get_category_display = serializers.CharField(read_only=True)
    is_ongoing = serializers.ReadOnlyField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "get_category_display",
            "thumbnail", "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = [
            "id", "get_category_display", "is_ongoing", "star_count",
            "is_starred", "starred_by_names",
        ]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        return strip_tags(value)


class EducationSerializer(StarredModelSerializer):
    year_range = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()

    class Meta:
        model = Education
        fields = [
            "id", "name", "degree", "description", "started_at", "ended_at",
            "year_range", "is_ongoing", "star_count", "is_starred",
            "starred_by_names",
        ]
        read_only_fields = [
            "id", "year_range", "is_ongoing", "star_count", "is_starred",
            "starred_by_names",
        ]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_degree(self, value):
        return strip_tags(value).strip()

    def validate_description(self, value):
        return strip_tags(value)


class SkillSerializer(StarredModelSerializer):
    tags = TagPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False,
    )

    class Meta:
        model = Skill
        fields = [
            "id", "title", "tags", "star_count", "is_starred",
            "starred_by_names",
        ]
        read_only_fields = [
            "id", "star_count", "is_starred", "starred_by_names",
        ]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value