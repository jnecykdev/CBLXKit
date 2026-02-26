# backend/cblxtool/concept/views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from page.models import Page
from .models import Concept


DEFAULT_CONCEPTS_BY_PHASE = {
    "Engage": [
        {"key": "big_idea", "label": "Big Idea", "order": 1},
        {"key": "essential_question", "label": "Essential Question", "order": 2},
        {"key": "challenge", "label": "Challenge", "order": 3},
    ],
    "Investigate": [
        {"key": "guiding_questions", "label": "Guiding Questions", "order": 1},
        {"key": "activities_resources", "label": "Activities & Resources", "order": 2},
        {"key": "synthesis", "label": "Synthesis", "order": 3},
    ],
    "Act": [
        {"key": "solution", "label": "Solution", "order": 1},
        {"key": "implementation", "label": "Implementation", "order": 2},
        {"key": "evaluation", "label": "Evaluation", "order": 3},
    ],
}


def _get_owned_page_or_404(page_id: int, request) -> Page:
    # Como Page não tem mais email, autorizamos via Project.email
    return get_object_or_404(Page, id=page_id, project__email=request.user.email)


def _serialize_concept(c: Concept) -> dict:
    return {
        "id": c.id,
        "page_id": c.page_id,
        "key": c.key,
        "label": c.label,
        "order": c.order,
        "icon": c.icon.url if c.icon else None,
        "content": c.content or [],
        "created_at": c.created_at.isoformat() if getattr(c, "created_at", None) else None,
        "updated_at": c.updated_at.isoformat() if getattr(c, "updated_at", None) else None,
    }


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def list_concepts_by_page(request, page_id: int):
    page = _get_owned_page_or_404(page_id, request)
    qs = Concept.objects.filter(page=page).order_by("order")
    return Response({"concepts": [_serialize_concept(c) for c in qs]}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def seed_page_concepts(request, page_id: int):
    page = _get_owned_page_or_404(page_id, request)

    defaults = DEFAULT_CONCEPTS_BY_PHASE.get(page.phase)
    if defaults is None:
        return Response({"error": f"Fase desconhecida: {page.phase}"}, status=status.HTTP_400_BAD_REQUEST)

    created = 0
    for item in defaults:
        obj, was_created = Concept.objects.get_or_create(
            page=page,
            key=item["key"],
            defaults={
                "label": item["label"],
                "order": item["order"],
                "content": [],
            },
        )
        if was_created:
            created += 1

    qs = Concept.objects.filter(page=page).order_by("order")
    return Response(
        {
            "message": "Concepts seeded",
            "created": created,
            "concepts": [_serialize_concept(c) for c in qs],
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def create_concept(request, page_id: int):
    page = _get_owned_page_or_404(page_id, request)

    key = (request.data.get("key") or "").strip()
    label = (request.data.get("label") or "").strip()
    order = request.data.get("order")
    content = request.data.get("content", [])

    if not key:
        return Response({"error": "Campo 'key' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    if not label:
        return Response({"error": "Campo 'label' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    if order is None:
        return Response({"error": "Campo 'order' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order_int = int(order)
    except Exception:
        return Response({"error": "Campo 'order' deve ser número inteiro."}, status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(content, list):
        return Response({"error": "Campo 'content' deve ser uma lista."}, status=status.HTTP_400_BAD_REQUEST)

    # unique_together(page, key)
    if Concept.objects.filter(page=page, key=key).exists():
        return Response({"error": f"Já existe concept com key='{key}' nesta page."}, status=status.HTTP_409_CONFLICT)

    concept = Concept.objects.create(
        page=page,
        key=key,
        label=label,
        order=order_int,
        content=content,
    )
    return Response({"concept": _serialize_concept(concept)}, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def update_concept(request, concept_id: int):
    concept = get_object_or_404(Concept, id=concept_id, page__project__email=request.user.email)

    if "label" in request.data:
        concept.label = str(request.data.get("label") or "").strip()

    if "order" in request.data:
        try:
            concept.order = int(request.data.get("order"))
        except Exception:
            return Response({"error": "Campo 'order' deve ser número inteiro."}, status=status.HTTP_400_BAD_REQUEST)

    if "content" in request.data:
        content = request.data.get("content")
        if not isinstance(content, list):
            return Response({"error": "Campo 'content' deve ser uma lista."}, status=status.HTTP_400_BAD_REQUEST)
        concept.content = content

    # key normalmente não deveria mudar, mas se você quiser permitir:
    if "key" in request.data:
        new_key = str(request.data.get("key") or "").strip()
        if not new_key:
            return Response({"error": "Campo 'key' não pode ser vazio."}, status=status.HTTP_400_BAD_REQUEST)
        if Concept.objects.filter(page=concept.page, key=new_key).exclude(id=concept.id).exists():
            return Response({"error": f"Já existe concept com key='{new_key}' nesta page."}, status=status.HTTP_409_CONFLICT)
        concept.key = new_key

    concept.save()
    return Response({"concept": _serialize_concept(concept)}, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def delete_concept(request, concept_id: int):
    concept = get_object_or_404(Concept, id=concept_id, page__project__email=request.user.email)
    concept.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
