from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities import Project, ProjectItem


class IProjectRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Project]:
        pass

    @abstractmethod
    def get_by_id(self, project_id: int) -> Optional[Project]:
        pass

    @abstractmethod
    def create(self, project: Project) -> Project:
        pass

    @abstractmethod
    def update(self, project: Project) -> Project:
        pass

    @abstractmethod
    def delete(self, project_id: int) -> bool:
        pass

    @abstractmethod
    def add_item(self, project_id: int, item: ProjectItem) -> ProjectItem:
        pass

    @abstractmethod
    def remove_item(self, item_id: int) -> bool:
        pass
