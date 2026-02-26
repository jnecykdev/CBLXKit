# page/services.py
from dataclasses import dataclass
from django.db import transaction
from .CBLpageDAO import CBLPageDAO
from .utils import salvar_html_fisico
from .constants import DEFAULT_DYNAMIC_DATA, MAX_PAGES_PER_PHASE
from phase.services import normalize_phase
from django.db.models import Max
from page.models import Page
from rest_framework.exceptions import PermissionDenied
from phase.models.phase import Phase

@dataclass
class PageService:
    dao: CBLPageDAO

    @transaction.atomic
    def create_page(self, owner, project_id: int, phase_raw: str):
        phase_name = normalize_phase(phase_raw)
        if not phase_name:
            raise ValueError("Fase inválida.")

        project = self.dao.get_project_accessible(project_id, owner)

        phase = Phase.objects.get_or_create(project=project, name=phase_name)[0]

        last = (
            Page.objects
            .select_for_update()
            .filter(project_id=project.id, phase=phase)
            .order_by("-order")
            .first()
        )
        next_order = (last.order + 1) if last else 1

        if next_order > MAX_PAGES_PER_PHASE:
            raise ValueError(f"Limite de {MAX_PAGES_PER_PHASE} páginas por fase atingido.")
    
        title = f"Página {next_order}"

        dynamic_data = DEFAULT_DYNAMIC_DATA[phase_name] if next_order == 1 else {}
        blocks = []

        page = self.dao.create_page(
            project=project,
            phase=phase,
            order=next_order,
            dynamic_data=dynamic_data,
            title=title,
            blocks=blocks,
            html="",
        )

        conteudo_para_html = dynamic_data if next_order == 1 else []
        salvar_html_fisico(owner.email, project.name, phase_name, next_order, conteudo_para_html)

        return page

    def list_pages_by_phase(self, project_id: int, phase_raw: str):
        phase_name = normalize_phase(phase_raw)
        if not phase_name:
            raise ValueError("Fase inválida.")

        return (
            Page.objects
            .filter(project=project_id, phase_name=phase_name)
            .order_by("order", "id")
        )

    @transaction.atomic
    def update_page(self, owner, page_id: int, payload: dict):
        page = self.dao.get_page_accessible(page_id, owner)

        title = payload.get("title")
        if title is not None:
            page.title = title

        if "blocks" in payload:
            blocks = payload.get("blocks")
            if blocks is None:
                blocks = []
            if not isinstance(blocks, list):
                raise ValueError("Blocks must be a list.")
            page.blocks = blocks

        if "dynamic_data" in payload:
            dynamic_data = payload.get("dynamic_data")
            if dynamic_data is None:
                dynamic_data = {}
            if not isinstance(dynamic_data, dict):
                raise ValueError("dynamic_data must be an object.")

            def normalize_dynamic_data(d: dict) -> dict:
                out = {}
                for k, v in (d or {}).items():
                    if isinstance(v, list):
                        norm = []
                        for item in v:
                            if isinstance(item, dict) and "content" in item:
                                norm.append({"content": str(item.get("content", ""))})
                            elif isinstance(item, str):
                                norm.append({"content": item})
                            else:
                                norm.append(item)
                        out[k] = norm
                    else:
                        out[k] = v
                return out

            page.dynamic_data = normalize_dynamic_data(dynamic_data)

        if "html" in payload:
            html = payload.get("html")
            if html is not None:
                page.html = html

        self.dao.save(page)

        project = page.project
        phase_name = page.phase_name

        # ALTERAR AQUI: não usar page.order para decidir
        if "blocks" in payload:
            conteudo_para_html = page.blocks or []
        elif "dynamic_data" in payload:
            conteudo_para_html = page.dynamic_data or {}
        else:
            conteudo_para_html = page.blocks or []

        salvar_html_fisico(owner.email, project.name, phase_name, page.order, conteudo_para_html)

        return page
    
    def get_page_data(self, owner, page_id: int):
        page = self.dao.get_page_accessible(page_id, owner)
        phase_name = page.phase_name

        if page.order == 1:
            defaults = DEFAULT_DYNAMIC_DATA.get(phase_name, {})
            data = {**defaults, **(page.dynamic_data or {})}
        else:
            data = page.dynamic_data or {}

        return {
            "id": page.id,
            "order": page.order,
            "phase": phase_name,
            "project_id": page.project_id,
            "dynamic_data": data,
            "blocks": page.blocks or [],
            "title": page.title,
            "html": page.html or "",
        }

    @transaction.atomic
    def update_html(self, owner, page_id: int, html: str):
        page = self.dao.get_page_accessible(page_id, owner)
        page.html = html
        page.save(update_fields=["html"])
        return page

    def update_page_state(self, user, page_id: int, payload: dict) -> Page:
        page = self.dao.get_page_accessible(page_id, user)
        if not page:
            raise PermissionDenied("Página não encontrada ou não autorizada.")
        
        allowed = {"title", "order", "dynamic_data", "blocks", "html"}
        for field in allowed:
            if field in payload:
                setattr(page, field, payload[field])

        page.save()
        return page
