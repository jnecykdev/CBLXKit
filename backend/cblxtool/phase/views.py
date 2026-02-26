# backend/cblxtool/phase/views.py
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from phase.models.phase import Phase
from .constants import DEFAULT_DYNAMIC_DATA

from page.serializers import PageSerializer
from rest_framework import status

from .services import (
    ensure_phase_and_page1,
    normalize_phase,
    get_project_for_user,
    list_pages_by_phase,
    get_phase_template_steps,
    PhaseNotFound,
    ProjectNotFoundOrUnauthorized,
)

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .constants import PHASE_ALIASES, STEP_MAP
from project.models import Project
from page.models import Page
# from phase.models.phase import Phase
from project.CBLprojectDAO import CBLProjectDAO
from django.utils import timezone
from datetime import timedelta

dao = CBLProjectDAO()

LOCK_TTL_SECONDS = 300

def _normalize_phase_name(phase_raw: str) -> str:
    key = (phase_raw or "").strip()
    return PHASE_ALIASES.get(key) or PHASE_ALIASES.get(key.lower()) or key


def _steps_payload_to_dynamic_data(phase_name: str, payload: dict) -> dict:
    
    steps = STEP_MAP.get(phase_name, [])
    dynamic_data = {}
    for step in steps:
        val = payload.get(step, [""])
        # garante lista de strings
        if isinstance(val, str):
            val = [val]
        elif val is None:
            val = [""]
        dynamic_data[step] = val
    return dynamic_data

def ensure_page1(project_id: int, phase_name: str) -> Page:
    phase = Phase.objects.get_or_create(project_id=project_id, name=phase_name)[0]

    page, created = Page.objects.get_or_create(
        project_id=project_id,
        phase=phase,
        order=1,
        defaults={
            "phase_name": phase.name,
            "title": (phase.name, "Página 1"),
            "dynamic_data": DEFAULT_DYNAMIC_DATA.get(phase.name, {}),
            "blocks": [],
            "html": "",
        }
    )
    return page

# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# @authentication_classes([TokenAuthentication])
# @transaction.atomic
# def get_phase(request, phase_name, project_id):
#     project_id = int(project_id)
#     phase_norm = normalize_phase(phase_name)

#     try:
#         _project = dao.get_project_accessible(project_id, request.user)
#     except ProjectNotFoundOrUnauthorized as e:
#         return Response({"error": str(e)}, status=403)

#     # ensure_page1(project_id, phase_norm)

#     pages_qs = (
#         Page.objects
#         .filter(project_id=project_id, phase_name=phase_norm)
#         .order_by("order", "id")
#     )

#     # dedupe por order: mantém sempre o menor id
#     seen_orders = set()
#     payload = []
#     for p in pages_qs:
#         if p.order in seen_orders:
#             continue
#         seen_orders.add(p.order)
#         payload.append({
#             "id": p.id,
#             "order": p.order,
#             "title": p.title,
#             "phase": p.phase_name,
#             "locked_by": getattr(p.locked_by, "email", None) if p.locked_by else None,
#             "editable": (p.locked_by == request.user.id) or (not p.locked_by) or p.locked_at(p),
#         })

#     return Response({"pages": payload}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@transaction.atomic
def get_phase(request, phase_name, project_id):
    project_id = int(project_id)
    phase_norm = normalize_phase(phase_name)

    try:
        _project = dao.get_project_accessible(project_id, request.user)
    except ProjectNotFoundOrUnauthorized as e:
        return Response({"error": str(e)}, status=403)

    ensure_page1(project_id, phase_norm)

    pages_qs = (
        Page.objects
        .filter(project_id=project_id, phase_name=phase_norm)
        .order_by("order", "id")
    )

    seen_orders = set()
    payload = []

    for p in pages_qs:
        if p.order in seen_orders:
            continue
        seen_orders.add(p.order)

        is_locked = bool(p.locked_by)
        mine = (p.locked_by == request.user)

        # usa sua função já existente no page/views.py
        expired = lock_expired(p) if is_locked else False

        editable = (not is_locked) or mine or expired

        payload.append({
            "id": p.id,
            "order": p.order,
            "title": p.title,
            "phase": p.phase_name,
            "locked_by": getattr(p.locked_by, "email", None) if p.locked_by else None,
            "editable": editable,
        })

    return Response({"pages": payload}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def get_phase_template(phase_name):
    try:
        phase = normalize_phase(phase_name)
        steps = get_phase_template_steps(phase)
        return Response({"steps": steps}, status=200)
    except PhaseNotFound:
        return Response({"error": "Invalid phase"}, status=400)
    
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def post_phase_data(request, phase_name):
    # normaliza nome da fase
    phase_name_norm = _normalize_phase_name(phase_name)

    # valida fase
    if phase_name_norm not in STEP_MAP:
        return Response({"error": "Invalid phase name"}, status=400)

    payload = request.data if isinstance(request.data, dict) else {}
    project_id = payload.get("project_id")
    page_id = payload.get("page_id")

    if not project_id or not page_id:
        return Response({"error": "project_id and page_id are required"}, status=400)

    # project = Project.objects.filter(id=project_id, owner__email=request.user.email).first()
    try:
        project = dao.get_project_accessible(int(project_id), request.user)
    except ProjectNotFoundOrUnauthorized as e:
        return Response({"error": str(e)}, status=403)

    if not project:
        return Response({"error": "Project not found or unauthorized."}, status=404)

    page = (
        Page.objects
        .filter(
            id=page_id,
            project=project,
            phase_name=phase_name_norm
        )
        .first()    
    )
    if not page:
        return Response({"error": "Page not found for this project/phase."}, status=404)

    # determina dynamic_data final
    incoming_dynamic = payload.get("dynamic_data")
    if isinstance(incoming_dynamic, dict):
        dynamic_data = incoming_dynamic
    else:
        dynamic_data = _steps_payload_to_dynamic_data(phase_name_norm, payload)

    try:
        with transaction.atomic():
            # merge seguro: mantém chaves existentes que não foram enviadas
            current = page.dynamic_data or {}
            dynamic_data = _strip_empty_arrays(dynamic_data)
            merged = {**current, **dynamic_data}
            page.dynamic_data = merged
            page.save(update_fields=["dynamic_data"])

        return Response({"message": f"{phase_name_norm} data saved successfully", "page_id": page.id}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

def _strip_empty_arrays(d: dict) -> dict:
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, list):
            # remove strings vazias e objetos {content:""} vazios
            filtered = []
            for item in v:
                if isinstance(item, dict) and "content" in item:
                    if str(item.get("content", "")).strip():
                        filtered.append(item)
                elif isinstance(item, str):
                    if item.strip():
                        filtered.append(item)
                else:
                    # mantém itens diferentes, se existirem
                    filtered.append(item)
            if filtered:
                out[k] = filtered
        else:
            # mantém valores não-lista
            out[k] = v
    return out

def lock_expired(page) -> bool:
    """
    Retorna True se o lock da página expirou.
    """
    if not page.locked_at:
        return False

    expires_at = page.locked_at + timedelta(seconds=LOCK_TTL_SECONDS)
    return timezone.now() >= expires_at