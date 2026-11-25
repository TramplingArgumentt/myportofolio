from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import (api_view, authentication_classes, permission_classes,)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from main.models import Education, Experience, Project, Skill, Tag
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.serializers import (
    EducationSerializer, ExperienceSerializer, ProjectSerializer, SkillSerializer,
    TagSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def tag_list(request):
    tags = Tag.objects.order_by("name", "id")
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_list(request):
    if request.method in ("GET", "HEAD"):
        projects = Project.objects.prefetch_related("tags", "starred_by").order_by("name", "id")
        name = request.query_params.get("name", "").strip()
        if name:
            projects = projects.filter(name__icontains=name)
        serializer = ProjectSerializer(
            projects, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = ProjectSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def project_detail(request, project_id):
    project = get_object_or_404(
        Project.objects.prefetch_related("tags" ,"starred_by"), pk=project_id,
    )
    if request.method in ("GET", "HEAD"):
        serializer = ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ProjectSerializer(
        project, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def project_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.starred_by.filter(pk=request.user.pk).exists():
        project.starred_by.remove(request.user)
    else:
        project.starred_by.add(request.user)
    serializer = ProjectSerializer(project, context={"request": request})
    return Response(serializer.data)


def _portfolio_list(request, model, serializer_class, search_field):
    items = model.objects.prefetch_related("starred_by")
    if model is Skill:
        items = items.prefetch_related("tags")
    search_query = request.query_params.get("name", "").strip()
    if search_query:
        items = items.filter(**{f"{search_field}__icontains": search_query})
    items = items.order_by(search_field, "id")

    if request.method in ("GET", "HEAD"):
        serializer = serializer_class(
            items, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = serializer_class(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def _portfolio_detail(request, model, serializer_class, object_id):
    items = model.objects.prefetch_related("starred_by")
    if model is Skill:
        items = items.prefetch_related("tags")
    item = get_object_or_404(items, pk=object_id)

    if request.method in ("GET", "HEAD"):
        serializer = serializer_class(item, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = serializer_class(
        item, data=request.data, partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


def _portfolio_star(request, model, serializer_class, object_id):
    item = get_object_or_404(model, pk=object_id)
    if item.starred_by.filter(pk=request.user.pk).exists():
        item.starred_by.remove(request.user)
    else:
        item.starred_by.add(request.user)
    serializer = serializer_class(item, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    return _portfolio_list(request, Experience, ExperienceSerializer, "title")


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    return _portfolio_detail(request, Experience, ExperienceSerializer, experience_id)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    return _portfolio_star(request, Experience, ExperienceSerializer, experience_id)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    return _portfolio_list(request, Education, EducationSerializer, "name")


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    return _portfolio_detail(request, Education, EducationSerializer, education_id)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    return _portfolio_star(request, Education, EducationSerializer, education_id)


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def skill_list(request):
    return _portfolio_list(request, Skill, SkillSerializer, "title")


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def skill_detail(request, skill_id):
    return _portfolio_detail(request, Skill, SkillSerializer, skill_id)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def skill_star(request, skill_id):
    return _portfolio_star(request, Skill, SkillSerializer, skill_id)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def api_logout(request):
    # TODO: Delete request.auth if it is not None, then return HTTP 204 No Content
    if request.auth is not None:
        request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)