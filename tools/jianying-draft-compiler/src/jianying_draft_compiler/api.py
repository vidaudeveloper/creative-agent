from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .catalog import list_effects, list_transitions
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


@app.get("/health")
def health() -> dict:
    return {"ok": True, "phase": "P0"}


@app.get("/catalog/transitions", response_model=list[CatalogItem])
def catalog_transitions() -> list[CatalogItem]:
    return [CatalogItem(name=i.name, kind=i.kind, is_vip=i.is_vip) for i in list_transitions()]


@app.get("/catalog/effects", response_model=list[CatalogItem])
def catalog_effects(q: str | None = None) -> list[CatalogItem]:
    items = list_effects()
    if q:
        items = [i for i in items if q in i.name]
    return [CatalogItem(name=i.name, kind=i.kind, is_vip=i.is_vip) for i in items]


@app.post("/edit-plan/validate")
def validate_plan(plan: EditPlan) -> dict:
    w, h = plan.canvas_size()
    return {"ok": True, "clips": len(plan.clips), "canvas": [w, h]}


@app.post("/edit-plan/compile", response_model=CompileResult)
def compile_plan(plan: EditPlan, make_zip: bool = True) -> CompileResult:
    try:
        return compile_edit_plan(plan, make_zip=make_zip)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
