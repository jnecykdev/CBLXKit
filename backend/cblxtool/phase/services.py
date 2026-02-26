# phase/services.py
from __future__ import annotations
from typing import List, Dict

from phase.models.phase import Phase
from project.models import Project
from page.models import Page
from django.db.models import Q
from .constants import PHASE_ALIASES, VALID_PHASES, STEP_MAP, PHASE_POSITION, DEFAULT_DYNAMIC_DATA
from django.db import transaction

from phase.phases.phaseEngage import PhaseEngage
from phase.phases.phaseInvestigate import PhaseInvestigate
from phase.phases.phaseAct import PhaseAct
from user.models import Profile


class PhaseNotFound(Exception):
    pass


class ProjectNotFoundOrUnauthorized(Exception):
    pass


def normalize_phase(phase_raw: str) -> str:
    """
    Normaliza alias e valida se a phase é uma das phases suportadas.
    """
    key = (phase_raw or "").strip()
    normalized = PHASE_ALIASES.get(key) or PHASE_ALIASES.get(key.lower())
    if not normalized or normalized not in VALID_PHASES:
        raise PhaseNotFound(f"Invalid phase: {phase_raw}")
    return normalized

def get_project_for_user(project_id: int, user_email: str):
    user = Profile.objects.filter(email=user_email).first()
    if not user:
        raise ProjectNotFoundOrUnauthorized()

    project = Project.objects.filter(
        Q(id=project_id) & (Q(owner=user) | Q(collaborators=user))
    ).distinct().first()

    if not project:
        raise ProjectNotFoundOrUnauthorized()

    return project

def get_or_create_project_phase(project: Project, phase_name: str) -> Phase:
    phase, _ = Phase.objects.get_or_create(project=project, name=phase_name)
    return phase

def list_pages_by_phase(project: Project, phase_name: str) -> List[Dict]:
    pages = (
        Page.objects
        .filter(project=project, phase_name=phase_name)
        .order_by("order", "id")
    )
    return [{"id": p.id, "order": p.order, "phase": p.phase_name, "title": p.title} for p in pages]

def get_phase_template_steps(phase_name: str) -> List[str]:
    try:
        return STEP_MAP[phase_name]
    except KeyError:
        raise PhaseNotFound(f"Invalid phase for steps: {phase_name}")

def list_project_phases(project: Project) -> List[Phase]:
    phases = list(project.phases.all())
    phases.sort(key=lambda ph: PHASE_POSITION.get(ph.name, 999))
    return phases

def ensure_project_phases_and_defaults(project: Project) -> None:
    engage = PhaseEngage.ensure_phase(project)
    PhaseEngage.ensure_default_pages(engage)

    investigate = PhaseInvestigate.ensure_phase(project)
    PhaseInvestigate.ensure_default_pages(investigate)

    act = PhaseAct.ensure_phase(project)
    PhaseAct.ensure_default_pages(act)

@transaction.atomic
def ensure_phase_and_page1(project, phase_name: str) -> Phase:
    phase, _ = Phase.objects.get_or_create(
        project=project,
        name=phase_name,
        defaults={
            "index": PHASE_POSITION.get(phase_name, 999),
            "description": "",
            "icon": "Sem Icone",
        },
    )

    Page.objects.get_or_create(
        project=project,
        phase=phase,
        order=1,
        defaults={
            "title": "Página 1",
            "dynamic_data": DEFAULT_DYNAMIC_DATA.get(phase_name, {}),
            "blocks": [],
            "html": "",
        },
    )
    return phase
