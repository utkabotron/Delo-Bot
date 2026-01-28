from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.application.dto import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectResponseDTO,
    ProjectItemCreateDTO,
    ProjectItemUpdateDTO,
    ProjectItemResponseDTO,
)
from app.application.use_cases import ProjectUseCases
from app.infrastructure.persistence.repositories import SQLAlchemyProjectRepository

router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_use_cases(db: Session = Depends(get_db)) -> ProjectUseCases:
    repository = SQLAlchemyProjectRepository(db)
    return ProjectUseCases(repository)


@router.get("", response_model=list[ProjectResponseDTO])
def get_projects(
    include_archived: bool = Query(False, description="Include archived projects"),
    use_cases: ProjectUseCases = Depends(get_use_cases),
):
    return use_cases.get_all_projects(include_archived=include_archived)


@router.post("", response_model=ProjectResponseDTO, status_code=201)
def create_project(
    dto: ProjectCreateDTO, use_cases: ProjectUseCases = Depends(get_use_cases)
):
    return use_cases.create_project(dto)


@router.get("/{project_id}", response_model=ProjectResponseDTO)
def get_project(
    project_id: int, use_cases: ProjectUseCases = Depends(get_use_cases)
):
    project = use_cases.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponseDTO)
def update_project(
    project_id: int,
    dto: ProjectUpdateDTO,
    use_cases: ProjectUseCases = Depends(get_use_cases),
):
    project = use_cases.update_project(project_id, dto)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int, use_cases: ProjectUseCases = Depends(get_use_cases)
):
    if not use_cases.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("/{project_id}/items", response_model=ProjectItemResponseDTO, status_code=201)
def add_item(
    project_id: int,
    dto: ProjectItemCreateDTO,
    use_cases: ProjectUseCases = Depends(get_use_cases),
):
    item = use_cases.add_item(project_id, dto)
    if not item:
        raise HTTPException(status_code=404, detail="Project not found")
    return item


@router.patch("/{project_id}/items/{item_id}", response_model=ProjectItemResponseDTO)
def update_item(
    project_id: int,
    item_id: int,
    dto: ProjectItemUpdateDTO,
    use_cases: ProjectUseCases = Depends(get_use_cases),
):
    item = use_cases.update_item_quantity(item_id, dto.quantity)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/{project_id}/items/{item_id}", status_code=204)
def remove_item(
    project_id: int,
    item_id: int,
    use_cases: ProjectUseCases = Depends(get_use_cases),
):
    if not use_cases.remove_item(item_id):
        raise HTTPException(status_code=404, detail="Item not found")


@router.get("/{project_id}/export")
def export_project(
    project_id: int,
    format: str = Query("text", description="Export format: 'text' or 'pdf'"),
    use_cases: ProjectUseCases = Depends(get_use_cases),
):
    if format == "pdf":
        pdf_buffer = use_cases.export_to_pdf(project_id)
        if not pdf_buffer:
            raise HTTPException(status_code=404, detail="Project not found")
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.pdf"},
        )
    else:
        text = use_cases.export_to_text(project_id)
        if not text:
            raise HTTPException(status_code=404, detail="Project not found")
        return PlainTextResponse(content=text)
