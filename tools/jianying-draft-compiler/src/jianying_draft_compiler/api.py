from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .catalog import (
    list_catalog,
    list_effects,
    list_filters,
    list_text_intros,
    list_text_outros,
    list_transitions,
    list_video_groups,
    list_video_intros,
    list_video_outros,
    validate_edit_plan_catalog,
)
from .compile import compile_edit_plan
from .models import CompileResult, EditPlan

app = FastAPI(
    title="jianying-draft-compiler",
    version="0.1.0",
    description="P0: Edit Plan → Jianying draft package (no effect rendering)",
)


class CatalogItem(BaseModel):
    name: str
    kind: str
    is_vip: bool | None = None


def _to_items(entries) -> list[CatalogItem]:
    return [CatalogItem(name=i.name, kind=i.kind, is_vip=i.is_vip) for i in entries]


@app.get("/health")
def health() -> dict:
    return {"ok": True, "phase": "P0"}


@app.get("/catalog/transitions", response_model=list[CatalogItem])
def catalog_transitions() -> list[CatalogItem]:
    return _to_items(list_transitions())


@app.get("/catalog/effects", response_model=list[CatalogItem])
def catalog_effects(
    q: str | None = None,
    kind: str = "all",
) -> list[CatalogItem]:
    if kind not in ("all", "scene", "character"):
        raise HTTPException(status_code=400, detail="kind must be all|scene|character")
    items = list_effects(kind=kind)  # type: ignore[arg-type]
    if q:
        items = [i for i in items if q in i.name]
    return _to_items(items)


@app.get("/catalog/filters", response_model=list[CatalogItem])
def catalog_filters(q: str | None = None, free: bool = False) -> list[CatalogItem]:
    items = list_filters()
    if free:
        items = [i for i in items if not i.is_vip]
    if q:
        items = [i for i in items if q in i.name]
    return _to_items(items)


@app.get("/catalog/video-animations", response_model=list[CatalogItem])
def catalog_video_animations(
    kind: str = "all",
    q: str | None = None,
    free: bool = False,
) -> list[CatalogItem]:
    items = []
    if kind in ("intro", "all"):
        items.extend(list_video_intros())
    if kind in ("outro", "all"):
        items.extend(list_video_outros())
    if kind in ("group", "all"):
        items.extend(list_video_groups())
    if free:
        items = [i for i in items if not i.is_vip]
    if q:
        items = [i for i in items if q in i.name]
    return _to_items(items)


@app.get("/catalog/text-animations", response_model=list[CatalogItem])
def catalog_text_animations(
    kind: str = "all",
    q: str | None = None,
    free: bool = False,
) -> list[CatalogItem]:
    items = []
    if kind in ("intro", "all"):
        items.extend(list_text_intros())
    if kind in ("outro", "all"):
        items.extend(list_text_outros())
    if free:
        items = [i for i in items if not i.is_vip]
    if q:
        items = [i for i in items if q in i.name]
    return _to_items(items)


@app.get("/catalog/{catalog_type}", response_model=list[CatalogItem])
def catalog_generic(
    catalog_type: str,
    q: str | None = None,
    kind: str = "all",
    free: bool = False,
    limit: int = 0,
) -> list[CatalogItem]:
    try:
        items = list_catalog(
            catalog_type,
            kind=kind,  # type: ignore[arg-type]
            grep=q or "",
            free=free,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return _to_items(items)


@app.post("/edit-plan/validate")
def validate_plan(plan: EditPlan) -> dict:
    w, h = plan.canvas_size()
    catalog_errors = validate_edit_plan_catalog(plan)
    if catalog_errors:
        return {
            "ok": False,
            "errors": catalog_errors,
            "clips": len(plan.clips),
            "canvas": [w, h],
        }
    return {"ok": True, "clips": len(plan.clips), "canvas": [w, h]}


@app.post("/edit-plan/compile", response_model=CompileResult)
def compile_plan(plan: EditPlan, make_zip: bool = True) -> CompileResult:
    try:
        return compile_edit_plan(plan, make_zip=make_zip)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
