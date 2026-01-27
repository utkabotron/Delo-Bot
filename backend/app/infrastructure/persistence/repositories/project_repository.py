from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from app.domain.entities import Project, ProjectItem
from app.domain.repositories import IProjectRepository
from app.infrastructure.persistence.models import ProjectModel, ProjectItemModel


class SQLAlchemyProjectRepository(IProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: ProjectModel) -> Project:
        items = [
            ProjectItem(
                id=item.id,
                project_id=item.project_id,
                name=item.name,
                item_type=item.item_type,
                base_price=Decimal(str(item.base_price)),
                cost_price=Decimal(str(item.cost_price)),
                quantity=item.quantity,
            )
            for item in model.items
        ]
        return Project(
            id=model.id,
            name=model.name,
            client=model.client,
            global_discount=Decimal(str(model.global_discount)),
            global_tax=Decimal(str(model.global_tax)),
            created_at=model.created_at,
            items=items,
        )

    def get_all(self) -> list[Project]:
        models = self.db.query(ProjectModel).order_by(ProjectModel.created_at.desc()).all()
        return [self._to_entity(m) for m in models]

    def get_by_id(self, project_id: int) -> Optional[Project]:
        model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def create(self, project: Project) -> Project:
        model = ProjectModel(
            name=project.name,
            client=project.client,
            global_discount=project.global_discount,
            global_tax=project.global_tax,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, project: Project) -> Project:
        model = self.db.query(ProjectModel).filter(ProjectModel.id == project.id).first()
        if model:
            model.name = project.name
            model.client = project.client
            model.global_discount = project.global_discount
            model.global_tax = project.global_tax
            self.db.commit()
            self.db.refresh(model)
            return self._to_entity(model)
        return project

    def delete(self, project_id: int) -> bool:
        model = self.db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False

    def add_item(self, project_id: int, item: ProjectItem) -> ProjectItem:
        model = ProjectItemModel(
            project_id=project_id,
            name=item.name,
            item_type=item.item_type,
            base_price=item.base_price,
            cost_price=item.cost_price,
            quantity=item.quantity,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return ProjectItem(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            item_type=model.item_type,
            base_price=Decimal(str(model.base_price)),
            cost_price=Decimal(str(model.cost_price)),
            quantity=model.quantity,
        )

    def remove_item(self, item_id: int) -> bool:
        model = self.db.query(ProjectItemModel).filter(ProjectItemModel.id == item_id).first()
        if model:
            self.db.delete(model)
            self.db.commit()
            return True
        return False

    def update_item_quantity(self, item_id: int, quantity: int) -> Optional[ProjectItem]:
        model = self.db.query(ProjectItemModel).filter(ProjectItemModel.id == item_id).first()
        if not model:
            return None
        model.quantity = quantity
        self.db.commit()
        self.db.refresh(model)
        return ProjectItem(
            id=model.id,
            project_id=model.project_id,
            name=model.name,
            item_type=model.item_type,
            base_price=Decimal(str(model.base_price)),
            cost_price=Decimal(str(model.cost_price)),
            quantity=model.quantity,
        )
