"""
Unit tests for Project and ProjectItem domain entities.
Tests the core business logic calculations.
"""
import pytest
from decimal import Decimal
from app.domain.entities import Project, ProjectItem


@pytest.mark.unit
class TestProjectItem:
    """Test ProjectItem calculations"""

    def test_subtotal_calculation(self):
        """Test item subtotal = base_price × quantity"""
        item = ProjectItem(
            name="Test Item",
            base_price=Decimal("100.50"),
            cost_price=Decimal("50.00"),
            quantity=3
        )
        assert item.subtotal == Decimal("301.50")

    def test_total_cost_calculation(self):
        """Test item total_cost = cost_price × quantity"""
        item = ProjectItem(
            name="Test Item",
            base_price=Decimal("100.00"),
            cost_price=Decimal("45.25"),
            quantity=4
        )
        assert item.total_cost == Decimal("181.00")

    def test_zero_quantity(self):
        """Test calculations with zero quantity"""
        item = ProjectItem(
            base_price=Decimal("100.00"),
            cost_price=Decimal("50.00"),
            quantity=0
        )
        assert item.subtotal == Decimal("0")
        assert item.total_cost == Decimal("0")

    def test_high_precision_decimals(self):
        """Test that decimal precision is preserved"""
        item = ProjectItem(
            base_price=Decimal("12.345"),
            cost_price=Decimal("5.678"),
            quantity=7
        )
        # 12.345 × 7 = 86.415
        assert item.subtotal == Decimal("86.415")
        # 5.678 × 7 = 39.746
        assert item.total_cost == Decimal("39.746")


@pytest.mark.unit
class TestProject:
    """Test Project calculations"""

    def test_empty_project(self):
        """Test project with no items"""
        project = Project(name="Empty Project")
        assert project.subtotal == Decimal("0")
        assert project.total_cost == Decimal("0")
        assert project.revenue == Decimal("0")
        assert project.profit == Decimal("0")
        assert project.margin == Decimal("0")

    def test_subtotal_with_multiple_items(self):
        """Test project subtotal = sum of item subtotals"""
        project = Project(
            name="Test Project",
            items=[
                ProjectItem(base_price=Decimal("100"), quantity=2),  # 200
                ProjectItem(base_price=Decimal("50"), quantity=3),   # 150
                ProjectItem(base_price=Decimal("75"), quantity=1),   # 75
            ]
        )
        assert project.subtotal == Decimal("425")

    def test_revenue_without_discount_or_tax(self):
        """Test revenue equals subtotal when no discount/tax"""
        project = Project(
            name="Test Project",
            global_discount=Decimal("0"),
            global_tax=Decimal("0"),
            items=[
                ProjectItem(base_price=Decimal("100"), quantity=2),
            ]
        )
        assert project.revenue == Decimal("200")

    def test_revenue_with_discount_only(self):
        """Test revenue with 10% discount (discount subtracts)"""
        project = Project(
            name="Test Project",
            global_discount=Decimal("10"),
            global_tax=Decimal("0"),
            items=[
                ProjectItem(base_price=Decimal("100"), quantity=1),
            ]
        )
        # 100 × (1 - 0.10) = 90
        assert project.revenue == Decimal("90")

    def test_revenue_with_tax_only(self):
        """Test revenue with 20% tax (tax also subtracts)"""
        project = Project(
            name="Test Project",
            global_discount=Decimal("0"),
            global_tax=Decimal("20"),
            items=[
                ProjectItem(base_price=Decimal("100"), quantity=1),
            ]
        )
        # 100 × (1 - 0.20) = 80
        assert project.revenue == Decimal("80")

    def test_revenue_with_both_discount_and_tax(self):
        """Test revenue with both discount (10%) and tax (15%)"""
        project = Project(
            name="Test Project",
            global_discount=Decimal("10"),
            global_tax=Decimal("15"),
            items=[
                ProjectItem(base_price=Decimal("1000"), quantity=1),
            ]
        )
        # 1000 × (1 - 0.10) × (1 - 0.15) = 1000 × 0.9 × 0.85 = 765
        assert project.revenue == Decimal("765")

    def test_total_cost_multiple_items(self):
        """Test total_cost = sum of item costs"""
        project = Project(
            name="Test Project",
            items=[
                ProjectItem(cost_price=Decimal("40"), quantity=2),   # 80
                ProjectItem(cost_price=Decimal("25"), quantity=3),   # 75
                ProjectItem(cost_price=Decimal("10"), quantity=5),   # 50
            ]
        )
        assert project.total_cost == Decimal("205")

    def test_profit_calculation(self):
        """Test profit = revenue - total_cost"""
        project = Project(
            name="Test Project",
            global_discount=Decimal("10"),
            global_tax=Decimal("0"),
            items=[
                ProjectItem(
                    base_price=Decimal("100"),
                    cost_price=Decimal("40"),
                    quantity=2
                ),
            ]
        )
        # revenue = 200 × 0.9 = 180
        # cost = 40 × 2 = 80
        # profit = 180 - 80 = 100
        assert project.revenue == Decimal("180")
        assert project.total_cost == Decimal("80")
        assert project.profit == Decimal("100")

    def test_negative_profit_loss(self):
        """Test project with negative profit (loss)"""
        project = Project(
            name="Loss Project",
            items=[
                ProjectItem(
                    base_price=Decimal("50"),
                    cost_price=Decimal("100"),  # Cost higher than price!
                    quantity=1
                ),
            ]
        )
        # revenue = 50
        # cost = 100
        # profit = -50 (loss)
        assert project.profit == Decimal("-50")

    def test_margin_calculation(self):
        """Test margin = (profit / revenue) × 100"""
        project = Project(
            name="Test Project",
            items=[
                ProjectItem(
                    base_price=Decimal("100"),
                    cost_price=Decimal("60"),
                    quantity=1
                ),
            ]
        )
        # revenue = 100
        # cost = 60
        # profit = 40
        # margin = (40/100) × 100 = 40%
        assert project.margin == Decimal("40")

    def test_margin_with_zero_revenue(self):
        """Test margin returns 0 when revenue is zero (prevent division by zero)"""
        project = Project(name="Zero Revenue")
        assert project.revenue == Decimal("0")
        assert project.margin == Decimal("0")

    def test_complex_scenario(self):
        """Test realistic scenario with multiple items, discount, and tax"""
        project = Project(
            name="Complex Project",
            client="ACME Corp",
            global_discount=Decimal("15"),
            global_tax=Decimal("10"),
            items=[
                ProjectItem(
                    name="Item A",
                    base_price=Decimal("250.00"),
                    cost_price=Decimal("120.00"),
                    quantity=3
                ),
                ProjectItem(
                    name="Item B",
                    base_price=Decimal("180.50"),
                    cost_price=Decimal("85.25"),
                    quantity=2
                ),
                ProjectItem(
                    name="Item C",
                    base_price=Decimal("99.99"),
                    cost_price=Decimal("45.00"),
                    quantity=5
                ),
            ]
        )

        # Subtotal = (250×3) + (180.5×2) + (99.99×5)
        #          = 750 + 361 + 499.95 = 1610.95
        assert project.subtotal == Decimal("1610.95")

        # Revenue = 1610.95 × (1-0.15) × (1-0.10)
        #         = 1610.95 × 0.85 × 0.90 = 1232.37675
        expected_revenue = Decimal("1232.37675")
        assert project.revenue == expected_revenue

        # Total cost = (120×3) + (85.25×2) + (45×5)
        #            = 360 + 170.5 + 225 = 755.5
        assert project.total_cost == Decimal("755.50")

        # Profit = 1232.37675 - 755.5 = 476.87675
        expected_profit = Decimal("476.87675")
        assert project.profit == expected_profit

        # Margin = (476.87675 / 1232.37675) × 100 ≈ 38.70%
        # Using quantize for approximate comparison
        assert project.margin.quantize(Decimal("0.01")) == Decimal("38.70")

    def test_discount_100_percent(self):
        """Test edge case: 100% discount means zero revenue"""
        project = Project(
            name="Free Project",
            global_discount=Decimal("100"),
            items=[
                ProjectItem(base_price=Decimal("100"), quantity=1),
            ]
        )
        # 100 × (1 - 1.00) = 0
        assert project.revenue == Decimal("0")

    def test_immutability_of_calculations(self):
        """Test that calculated properties don't modify state"""
        project = Project(
            name="Test",
            items=[ProjectItem(base_price=Decimal("100"), quantity=1)]
        )

        # Call properties multiple times
        _ = project.subtotal
        _ = project.revenue
        _ = project.profit
        _ = project.margin

        # Verify state unchanged
        assert len(project.items) == 1
        assert project.global_discount == Decimal("0")
