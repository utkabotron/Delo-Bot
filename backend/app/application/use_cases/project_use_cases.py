from typing import Optional
from app.domain.entities import Project, ProjectItem
from app.domain.repositories import IProjectRepository
from app.application.dto import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectResponseDTO,
    ProjectItemCreateDTO,
    ProjectItemResponseDTO,
    ProjectSummaryDTO,
)


class ProjectUseCases:
    def __init__(self, repository: IProjectRepository):
        self.repository = repository

    def _to_response(self, project: Project) -> ProjectResponseDTO:
        items = [
            ProjectItemResponseDTO(
                id=item.id,
                name=item.name,
                item_type=item.item_type,
                base_price=item.base_price,
                cost_price=item.cost_price,
                quantity=item.quantity,
                subtotal=item.subtotal,
                total_cost=item.total_cost,
            )
            for item in project.items
        ]
        summary = ProjectSummaryDTO(
            subtotal=project.subtotal,
            revenue=project.revenue,
            total_cost=project.total_cost,
            profit=project.profit,
            margin=project.margin,
        )
        return ProjectResponseDTO(
            id=project.id,
            name=project.name,
            client=project.client,
            global_discount=project.global_discount,
            global_tax=project.global_tax,
            created_at=project.created_at,
            items=items,
            summary=summary,
        )

    def get_all_projects(self) -> list[ProjectResponseDTO]:
        projects = self.repository.get_all()
        return [self._to_response(p) for p in projects]

    def get_project(self, project_id: int) -> Optional[ProjectResponseDTO]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None
        return self._to_response(project)

    def create_project(self, dto: ProjectCreateDTO) -> ProjectResponseDTO:
        project = Project(
            name=dto.name,
            client=dto.client,
            global_discount=dto.global_discount,
            global_tax=dto.global_tax,
        )
        created = self.repository.create(project)
        return self._to_response(created)

    def update_project(
        self, project_id: int, dto: ProjectUpdateDTO
    ) -> Optional[ProjectResponseDTO]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        if dto.name is not None:
            project.name = dto.name
        if dto.client is not None:
            project.client = dto.client
        if dto.global_discount is not None:
            project.global_discount = dto.global_discount
        if dto.global_tax is not None:
            project.global_tax = dto.global_tax

        updated = self.repository.update(project)
        return self._to_response(updated)

    def delete_project(self, project_id: int) -> bool:
        return self.repository.delete(project_id)

    def add_item(
        self, project_id: int, dto: ProjectItemCreateDTO
    ) -> Optional[ProjectItemResponseDTO]:
        project = self.repository.get_by_id(project_id)
        if not project:
            return None

        item = ProjectItem(
            name=dto.name,
            item_type=dto.item_type,
            base_price=dto.base_price,
            cost_price=dto.cost_price,
            quantity=dto.quantity,
        )
        created = self.repository.add_item(project_id, item)
        return ProjectItemResponseDTO(
            id=created.id,
            name=created.name,
            item_type=created.item_type,
            base_price=created.base_price,
            cost_price=created.cost_price,
            quantity=created.quantity,
            subtotal=created.subtotal,
            total_cost=created.total_cost,
        )

    def remove_item(self, item_id: int) -> bool:
        return self.repository.remove_item(item_id)

    def update_item_quantity(self, item_id: int, quantity: int) -> Optional[ProjectItemResponseDTO]:
        item = self.repository.update_item_quantity(item_id, quantity)
        if not item:
            return None
        return ProjectItemResponseDTO(
            id=item.id,
            name=item.name,
            item_type=item.item_type,
            base_price=item.base_price,
            cost_price=item.cost_price,
            quantity=item.quantity,
            subtotal=item.subtotal,
            total_cost=item.total_cost,
        )
