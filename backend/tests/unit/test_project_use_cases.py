"""
Unit tests for ProjectUseCases.
Tests use mocked repositories to isolate business logic.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, MagicMock
from app.domain.entities import Project, ProjectItem
from app.application.use_cases import ProjectUseCases
from app.application.dto import (
    ProjectCreateDTO,
    ProjectUpdateDTO,
    ProjectItemCreateDTO,
)


@pytest.fixture
def mock_repository():
    """Create a mocked IProjectRepository"""
    return Mock()


@pytest.fixture
def use_cases(mock_repository):
    """Create ProjectUseCases with mocked repository"""
    return ProjectUseCases(repository=mock_repository)


@pytest.fixture
def sample_project():
    """Create a sample Project entity for testing"""
    return Project(
        id=1,
        name="Test Project",
        client="ACME Corp",
        global_discount=Decimal("10"),
        global_tax=Decimal("5"),
        created_at=datetime(2026, 1, 1, 12, 0, 0),
        items=[
            ProjectItem(
                id=1,
                project_id=1,
                name="Item A",
                base_price=Decimal("100"),
                cost_price=Decimal("50"),
                quantity=2
            ),
            ProjectItem(
                id=2,
                project_id=1,
                name="Item B",
                base_price=Decimal("200"),
                cost_price=Decimal("80"),
                quantity=1
            ),
        ]
    )


@pytest.mark.unit
class TestProjectUseCases:
    """Test ProjectUseCases business logic"""

    def test_get_all_projects(self, use_cases, mock_repository, sample_project):
        """Test getting all projects"""
        # Arrange
        projects = [sample_project]
        mock_repository.get_all.return_value = projects

        # Act
        result = use_cases.get_all_projects()

        # Assert
        mock_repository.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].name == "Test Project"
        assert result[0].client == "ACME Corp"
        assert len(result[0].items) == 2
        # Verify summary calculations
        assert result[0].summary.subtotal == Decimal("400")  # (100*2) + (200*1)

    def test_get_project_exists(self, use_cases, mock_repository, sample_project):
        """Test getting a single project that exists"""
        # Arrange
        mock_repository.get_by_id.return_value = sample_project

        # Act
        result = use_cases.get_project(project_id=1)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(1)
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Project"

    def test_get_project_not_found(self, use_cases, mock_repository):
        """Test getting a project that doesn't exist"""
        # Arrange
        mock_repository.get_by_id.return_value = None

        # Act
        result = use_cases.get_project(project_id=999)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(999)
        assert result is None

    def test_create_project(self, use_cases, mock_repository):
        """Test creating a new project"""
        # Arrange
        dto = ProjectCreateDTO(
            name="New Project",
            client="New Client",
            global_discount=Decimal("15"),
            global_tax=Decimal("8")
        )
        created_project = Project(
            id=123,
            name=dto.name,
            client=dto.client,
            global_discount=dto.global_discount,
            global_tax=dto.global_tax,
            items=[]
        )
        mock_repository.create.return_value = created_project

        # Act
        result = use_cases.create_project(dto)

        # Assert
        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args[0][0]
        assert isinstance(call_args, Project)
        assert call_args.name == "New Project"
        assert call_args.client == "New Client"
        assert result.id == 123
        assert result.name == "New Project"

    def test_update_project_partial(self, use_cases, mock_repository, sample_project):
        """Test updating only some fields of a project"""
        # Arrange
        mock_repository.get_by_id.return_value = sample_project
        updated_project = Project(
            id=1,
            name="Updated Name",
            client="ACME Corp",
            global_discount=Decimal("10"),
            global_tax=Decimal("5"),
            items=sample_project.items
        )
        mock_repository.update.return_value = updated_project

        dto = ProjectUpdateDTO(name="Updated Name")

        # Act
        result = use_cases.update_project(project_id=1, dto=dto)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.update.assert_called_once()
        assert result is not None
        assert result.name == "Updated Name"

    def test_update_project_not_found(self, use_cases, mock_repository):
        """Test updating a project that doesn't exist"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        dto = ProjectUpdateDTO(name="Updated")

        # Act
        result = use_cases.update_project(project_id=999, dto=dto)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(999)
        mock_repository.update.assert_not_called()
        assert result is None

    def test_delete_project_success(self, use_cases, mock_repository):
        """Test deleting a project"""
        # Arrange
        mock_repository.delete.return_value = True

        # Act
        result = use_cases.delete_project(project_id=1)

        # Assert
        mock_repository.delete.assert_called_once_with(1)
        assert result is True

    def test_delete_project_not_found(self, use_cases, mock_repository):
        """Test deleting a non-existent project"""
        # Arrange
        mock_repository.delete.return_value = False

        # Act
        result = use_cases.delete_project(project_id=999)

        # Assert
        mock_repository.delete.assert_called_once_with(999)
        assert result is False

    def test_add_item_to_project(self, use_cases, mock_repository, sample_project):
        """Test adding an item to a project"""
        # Arrange
        mock_repository.get_by_id.return_value = sample_project
        dto = ProjectItemCreateDTO(
            name="New Item",
            item_type="Widget",
            base_price=Decimal("150"),
            cost_price=Decimal("75"),
            quantity=3
        )
        created_item = ProjectItem(
            id=3,
            project_id=1,
            name=dto.name,
            item_type=dto.item_type,
            base_price=dto.base_price,
            cost_price=dto.cost_price,
            quantity=dto.quantity
        )
        mock_repository.add_item.return_value = created_item

        # Act
        result = use_cases.add_item(project_id=1, dto=dto)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.add_item.assert_called_once()
        assert result is not None
        assert result.id == 3
        assert result.name == "New Item"
        assert result.subtotal == Decimal("450")  # 150 * 3

    def test_add_item_project_not_found(self, use_cases, mock_repository):
        """Test adding an item to non-existent project"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        dto = ProjectItemCreateDTO(
            name="Item",
            base_price=Decimal("100"),
            cost_price=Decimal("50"),
            quantity=1
        )

        # Act
        result = use_cases.add_item(project_id=999, dto=dto)

        # Assert
        mock_repository.get_by_id.assert_called_once_with(999)
        mock_repository.add_item.assert_not_called()
        assert result is None

    def test_remove_item(self, use_cases, mock_repository):
        """Test removing an item"""
        # Arrange
        mock_repository.remove_item.return_value = True

        # Act
        result = use_cases.remove_item(item_id=1)

        # Assert
        mock_repository.remove_item.assert_called_once_with(1)
        assert result is True

    def test_update_item_quantity(self, use_cases, mock_repository):
        """Test updating item quantity"""
        # Arrange
        updated_item = ProjectItem(
            id=1,
            project_id=1,
            name="Item",
            base_price=Decimal("100"),
            cost_price=Decimal("50"),
            quantity=5  # Updated quantity
        )
        mock_repository.update_item_quantity.return_value = updated_item

        # Act
        result = use_cases.update_item_quantity(item_id=1, quantity=5)

        # Assert
        mock_repository.update_item_quantity.assert_called_once_with(1, 5)
        assert result is not None
        assert result.quantity == 5
        assert result.subtotal == Decimal("500")  # 100 * 5

    def test_update_item_quantity_not_found(self, use_cases, mock_repository):
        """Test updating quantity of non-existent item"""
        # Arrange
        mock_repository.update_item_quantity.return_value = None

        # Act
        result = use_cases.update_item_quantity(item_id=999, quantity=5)

        # Assert
        mock_repository.update_item_quantity.assert_called_once_with(999, 5)
        assert result is None
